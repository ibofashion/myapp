## Context

Voir proposal.md - Why. `core/models.py` a déjà `Sale.seller` et `User.role`. `core/views.py` a déjà `sale_create`/`sale_detail` et le formset `SaleLineFormSet` (`core/forms.py`) utilisé pour créer une vente avec ses lignes. Aucune vue d'édition/suppression, ni `core/authz.py`, n'existent encore. ARCHITECTURE.md §4.2 et §5 fixent déjà l'invariant de suppression et la signature de `can_edit_sale` — ce document ne fait qu'appliquer ces décisions actées, il ne les rouvre pas.

## Goals / Non-Goals

**Goals:**
- Une fonction d'autorisation unique, testée isolément, réutilisée par toutes les vues sensibles sur `Sale`.
- Réutiliser le formset existant (`SaleLineFormSet`) pour l'édition, plutôt que dupliquer la logique de validation des lignes.
- Suppression bloquée de façon atomique si des `PaymentAllocation` existent, sans race condition entre la vérification et la suppression.

**Non-Goals:**
- Historique/traçabilité des modifications (hors périmètre produit, cf. CLAUDE.md).
- Retrait ou réimputation des `PaymentAllocation` depuis l'écran d'annulation (le message renvoie l'utilisateur au flux de paiement existant ; réimputer n'est pas construit ici).
- Édition du client ou du vendeur d'une vente existante — seules les lignes (article/prix/quantité) sont modifiables.
- Gestion des comptes vendeurs (déjà couverte par Django Admin, capability `vendeur-accounts`).

## Decisions

- **`can_edit_sale(user, sale)` dans `core/authz.py`**, exactement comme spécifié en ARCHITECTURE.md §5 (`role == "admin" or sale.seller_id == user.id`). Appelée en tête des vues `sale_edit`/`sale_delete`, qui renvoient `PermissionDenied` (→ 403) si elle échoue. Alternative écartée : dupliquer le test inline dans chaque vue — rejetée car CLAUDE.md interdit explicitement de dupliquer ce contrôle.
- **Vue d'édition basée sur `SaleLineFormSet` existant**, en réutilisant les mêmes règles de validation (min 1 ligne, prix ≥ 0, quantité > 0) que `sale_create`. Le client et le vendeur de la vente restent en lecture seule sur cet écran ; seules les lignes sont éditables. Alternative écartée : formulaire d'édition entièrement séparé — rejetée, ferait diverger les règles de validation entre création et édition.
- **Suppression dans `transaction.atomic()` avec re-vérification de l'absence d'allocations juste avant `sale.delete()`**, suivant le patron déjà en place pour `record_payment` (ARCHITECTURE.md §4.1) qui utilise `select_for_update()`. Empêche qu'un paiement soit imputé entre l'affichage du bouton « Annuler » et la confirmation de suppression.
- **Boutons « Modifier »/« Annuler » conditionnés côté template par `can_edit_sale`**, uniquement pour l'ergonomie (éviter de proposer une action qui sera de toute façon refusée) — jamais comme seule protection, conformément à ARCHITECTURE.md §5.

## Risks / Trade-offs

- [Une vente en cours de modification par un vendeur pourrait être annulée entre-temps par un admin sur un autre appareil] → hors périmètre de ce changement (pas de verrouillage optimiste demandé) ; la resoumission d'un formulaire pointant vers une vente supprimée renverra une 404 classique.
- [Réutiliser `SaleLineFormSet` en mode édition suppose qu'il gère correctement les lignes existantes (suppression via `DELETE` du formset) en plus de l'ajout] → à vérifier en tâche d'implémentation ; sinon ajuster le formset plutôt qu'en créer un second.
