# Architecture — Mini CRM de gestion des ventes à crédit

Document de référence des choix techniques retenus pour l'implémentation. Découle du [`PRD.md`](./PRD.md).

---

## 1. Stack technique

| Couche | Choix |
|---|---|
| Langage | Python 3.12+ |
| Framework | Django 5 (LTS) |
| Base de données | PostgreSQL |
| ORM | Django ORM (migrations natives) |
| Interactivité front | HTMX + Alpine.js (pas de SPA) |
| CSS | Tailwind CSS (CDN pour le MVP — bascule vers `django-tailwind` si le CDN devient limitant) |
| Auth | `django.contrib.auth`, sessions, provider identifiant/mot de passe |
| Admin | Django Admin, pour la gestion des comptes vendeurs (V1) |
| Tests | `pytest-django` (logique métier) + Playwright (parcours utilisateur) |
| Gestion des dépendances | `pip` + `venv` (`requirements.txt`) |
| Hébergement | Railway Hobby (5 $/mois) — app + PostgreSQL sur la même plateforme |
| Devise | **XOF (franc CFA)** — pas de sous-unité |

---

## 2. Modèle de données

```python
# users
class User(AbstractUser):
    ROLE_CHOICES = [("vendeur", "Vendeur"), ("admin", "Admin")]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="vendeur")

# clients
class Client(models.Model):
    phone = models.CharField(max_length=20, unique=True)  # normalisé E.164 avant écriture
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

# sales
class Sale(models.Model):
    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name="sales")
    seller = models.ForeignKey(User, on_delete=models.PROTECT, related_name="sales")
    sold_at = models.DateTimeField(auto_now_add=True)

# sale_lines
class SaleLine(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name="lines")
    label = models.CharField(max_length=200)             # texte libre, pas de catalogue
    unit_price = models.DecimalField(max_digits=12, decimal_places=0)
    quantity = models.PositiveIntegerField()

# payments
class Payment(models.Model):
    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name="payments")
    amount = models.DecimalField(max_digits=12, decimal_places=0)
    paid_at = models.DateTimeField(auto_now_add=True)
    recorded_by = models.ForeignKey(User, on_delete=models.PROTECT)

# payment_allocations
class PaymentAllocation(models.Model):
    payment = models.ForeignKey(Payment, on_delete=models.PROTECT, related_name="allocations")
    sale = models.ForeignKey(Sale, on_delete=models.PROTECT, related_name="allocations")
    amount = models.DecimalField(max_digits=12, decimal_places=0)

    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(amount__gt=0), name="allocation_amount_positive"),
        ]
```

**Notes de conception**

- Montants en `DecimalField(max_digits=12, decimal_places=0)` : cohérent avec le XOF, exact par nature (contrairement à un `float`).
- `clients.phone` : normaliser en E.164 (ou format local strict) **avant** insertion — sinon la clé unique du §2.3 du PRD ne protège rien contre deux écritures différentes du même numéro.
- Pas de table `articles` (conforme au §2.2 — prix négociables, pas de catalogue). L'autocomplétion V2 du « dernier prix pratiqué » se fait par requête `DISTINCT ON (label) ... ORDER BY label, sold_at DESC` sur `SaleLine`, sans table dédiée.
- Pas de table d'historique/audit (conforme au §2.2 — « pas de traçabilité »). Ne pas en ajouter une non demandée.
- `on_delete=PROTECT` partout où une suppression amont casserait une donnée financière avale (client, vendeur) — la suppression en cascade n'est autorisée que des lignes de vente vers leur vente (`SaleLine.sale`, `CASCADE`), voir §4 pour la suppression d'une vente elle-même.
- Index sur `sales.client_id`, `sale_lines.sale_id`, `payment_allocations.sale_id`, `payment_allocations.payment_id` (`db_index=True` ou `Meta.indexes`).

---

## 3. Calculs dérivés : vue SQL

Le §5 du PRD est explicite : total ligne, total vente, solde, statut ne doivent jamais être stockés en dur. Une **vue PostgreSQL**, créée par migration (`migrations.RunSQL`), est l'unique source de vérité :

```sql
CREATE VIEW v_sale_balances AS
SELECT
  s.id AS sale_id,
  s.client_id,
  COALESCE(l.total, 0)                          AS total,
  COALESCE(a.paid, 0)                           AS paid,
  COALESCE(l.total, 0) - COALESCE(a.paid, 0)    AS balance,
  CASE
    WHEN COALESCE(a.paid, 0) = 0                     THEN 'non_paye'
    WHEN COALESCE(a.paid, 0) >= COALESCE(l.total, 0) THEN 'solde'
    ELSE 'partiel'
  END                                            AS status
FROM sales s
LEFT JOIN (SELECT sale_id, SUM(unit_price * quantity) AS total
           FROM sale_lines GROUP BY sale_id) l ON l.sale_id = s.id
LEFT JOIN (SELECT sale_id, SUM(amount) AS paid
           FROM payment_allocations GROUP BY sale_id) a ON a.sale_id = s.id;
```

Exposée côté ORM par un modèle non managé :

```python
class SaleBalance(models.Model):
    sale = models.OneToOneField(Sale, primary_key=True, db_column="sale_id", on_delete=models.DO_NOTHING)
    client_id = models.IntegerField()
    total = models.DecimalField(max_digits=12, decimal_places=0)
    paid = models.DecimalField(max_digits=12, decimal_places=0)
    balance = models.DecimalField(max_digits=12, decimal_places=0)
    status = models.CharField(max_length=10)

    class Meta:
        managed = False
        db_table = "v_sale_balances"
```

La dette totale d'un client et le tableau de bord (V1/V2) se déduisent d'une agrégation Django (`SaleBalance.objects.filter(...).aggregate(...)`) sur cette vue — jamais d'un champ `total_du` recalculé à la main lors d'un paiement.

---

## 4. Règles métier et invariants

### 4.1 Imputation d'un paiement

Opération la plus sensible de l'app (§2.2 du PRD : répartition manuelle sur une ou plusieurs ventes précises). Exécutée dans un bloc `transaction.atomic()`, avec verrouillage des ventes concernées via `select_for_update()` :

```python
from django.db import transaction

@transaction.atomic
def record_payment(client: Client, amount: Decimal, allocations: list[tuple[Sale, Decimal]], recorded_by: User) -> Payment:
    sale_ids = [sale.id for sale, _ in allocations]
    locked_sales = {s.id: s for s in Sale.objects.select_for_update().filter(id__in=sale_ids, client=client)}
    # invariants ci-dessous, puis création de Payment + PaymentAllocation
```

Invariants vérifiés avant commit :

- `SUM(allocations d'un paiement) == payment.amount` — tout le paiement est réparti, rien ne se perd.
- `SUM(allocations existantes + nouvelles d'une vente) <= total de la vente` — jamais de sur-paiement.
- Chaque `amount` d'allocation est `> 0` (doublé par la contrainte `CHECK` sur `PaymentAllocation`, §2).
- Toutes les ventes visées appartiennent bien au client du paiement.

### 4.2 Suppression d'une vente

Une vente annulée (§2.4 du PRD) est **définitivement supprimée**, pas archivée. Garde-fou obligatoire : une vente ayant déjà des `PaymentAllocation` ne peut pas être supprimée directement — il faut d'abord retirer/réimputer ces allocations, sinon le paiement source ne serait plus intégralement réparti (invariant §4.1 violé côté paiement).

```python
def delete_sale(sale: Sale, requested_by: User) -> None:
    if not can_edit_sale(requested_by, sale):
        raise PermissionDenied
    if sale.allocations.exists():
        raise ValidationError(
            "Cette vente a des paiements imputés dessus : retirez d'abord ces imputations avant de l'annuler."
        )
    sale.delete()  # CASCADE sur SaleLine
```

---

## 5. Autorisation

Une seule fonction `can_edit_sale(user, sale)` (`core/authz.py`), appelée par **toutes** les vues de modification/annulation de vente — jamais dupliquée dans les templates :

```python
def can_edit_sale(user: User, sale: Sale) -> bool:
    return user.role == "admin" or sale.seller_id == user.id
```

Appliquée en tête de vue (ou via `UserPassesTestMixin` sur les vues à base de classe). Le contrôle vit **côté serveur** : cacher un bouton « modifier » dans le template pour un vendeur n'est pas une autorisation — un accès direct à l'URL contournerait tout.

Rôle porté par un champ `role` sur `User` (`vendeur`/`admin`) plutôt que le système `Group`/`Permission` complet de Django, sur-dimensionné pour deux rôles fixes.

---

## 6. Résilience réseau

Une boutique n'a pas toujours une connexion fiable :

- Boutons de soumission désactivés pendant l'envoi (`hx-disabled-elt`) + indicateur de chargement (`hx-indicator`).
- **Clé d'idempotence** sur la création de vente et de paiement (générée côté client, envoyée avec la requête) → un double-tap sur un réseau lent ne crée pas deux ventes identiques.
- Messages d'erreur réseau explicites plutôt qu'un formulaire qui semble ne rien faire.

---

## 7. Hébergement

- **Railway Hobby (5 $/mois)** : héberge l'app Django et PostgreSQL sur une seule plateforme, une seule facture. Pas de configuration serverless à apprendre.
- Écarté : les paliers gratuits de Render (mise en veille après 15 min d'inactivité, redémarrage à froid 30–60 s — inacceptable pour un vendeur au comptoir) et de Railway/Fly.io (retirés pour les nouveaux comptes en 2026).

---

## 8. Tests

Test de fumée à couvrir dès les premiers écrans (`pytest-django`, sur `v_sale_balances`) :

1. Créer une vente de 10 000 → `balance = 10000`, `status = 'non_paye'`.
2. Imputer un paiement de 4 000 → `balance = 6000`, `status = 'partiel'`.
3. Imputer 6 000 de plus → `balance = 0`, `status = 'solde'`.
4. Tenter d'imputer 1 de plus sur cette vente → rejet (violation de l'invariant de sur-paiement).
5. Tenter de supprimer une vente ayant une allocation → rejet (§4.2).

---

## 9. Décisions actées avec le porteur du projet

| Question | Décision |
|---|---|
| Devise | XOF (franc CFA), montants entiers sans décimale |
| Suppression d'une vente annulée | Suppression définitive (pas d'archivage), bloquée si des paiements y sont déjà imputés |
| Gestion des dépendances Python | `pip` + `venv` |

Aucun point bloquant restant à ce stade. Le format exact de normalisation du numéro de téléphone (E.164 strict vs format local) et le choix `django-tailwind` vs CDN Tailwind sont des détails d'implémentation à trancher au moment du scaffolding, sans impact sur l'architecture ci-dessus.
