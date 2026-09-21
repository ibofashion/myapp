## Context

`SaleBalance` (`core/models.py`) est un modèle non managé adossé à la vue SQL `v_sale_balances` (voir ARCHITECTURE.md §3) et expose déjà `balance`/`status` par vente, dérivés sans stockage en dur. `Payment` est enregistré par client avec une date. Voir proposal.md - Why pour la motivation.

## Goals / Non-Goals

**Goals:**
- Calculer tous les totaux du tableau de bord par agrégation Django sur `SaleBalance` et `Payment`, sans nouveau champ stocké.
- Garder la page rapide avec un nombre borné de requêtes (pas de N+1 par client).

**Non-Goals:**
- Filtrage par vendeur, export, ou plage de dates libre (voir V2, hors périmètre confirmé avec le porteur de produit).
- Historique ou graphique d'évolution — uniquement des totaux instantanés.

## Decisions

- **Dette globale et par client** : une seule requête `SaleBalance.objects.filter(balance__gt=0).values("client_id", "client__name").annotate(total_due=Sum("balance"))` sert à la fois la dette globale (somme des `total_due`) et le détail par client (les lignes du groupement), évitant une requête par client.
- **Bornes de période** : calculer les bornes « aujourd'hui / cette semaine / ce mois » côté serveur avec `django.utils.timezone.localtime(timezone.now())`, puis filtrer `Payment.objects.filter(paid_at__gte=debut, paid_at__lt=fin)`, pour rester cohérent avec le fuseau horaire configuré du projet plutôt que de recalculer côté client.
- **Préset par défaut** : « aujourd'hui », choisi via un paramètre de requête GET (ex. `?periode=semaine`) plutôt qu'un état de session, pour que l'URL du tableau de bord reste partageable/rechargeable sans effet de bord.

## Risks / Trade-offs

- [Agrégation sur `SaleBalance` à chaque chargement de page peut devenir coûteuse avec un grand volume de ventes] → Acceptable pour le volume actuel d'une boutique unique ; à revisiter (mise en cache) seulement si mesuré comme un problème réel, pas préventivement.
- [Le préset « cette semaine » dépend d'une convention de début de semaine] → Utiliser la convention locale de Django (`timezone.localtime` + `isoweekday`), cohérente avec le reste de l'application ; pas de configuration exposée à l'utilisateur pour rester « basique ».
