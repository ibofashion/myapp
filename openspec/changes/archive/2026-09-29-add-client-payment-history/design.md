## Context

`Payment` et `PaymentAllocation` sont déjà enregistrés à chaque paiement (voir `record_payment`, ARCHITECTURE.md §4.1), mais la fiche client (`client_detail`) n'affiche que les ventes et leurs soldes (`SaleBalance`), jamais l'historique des paiements eux-mêmes. Voir proposal.md - Why pour la motivation.

## Goals / Non-Goals

**Goals:**
- Afficher l'historique complet des paiements d'un client directement depuis les données déjà stockées (`Payment`, `PaymentAllocation`), sans recalcul ni duplication de valeur financière.
- Garder la page performante quel que soit le nombre de paiements/imputations (pas de requêtes N+1).

**Non-Goals:**
- Édition ou suppression de paiement depuis cet historique (portée strictement lecture seule, cf. proposal.md).
- Affichage équivalent sur la fiche vente (décision de périmètre déjà validée avec l'utilisateur, cf. proposal.md).

## Decisions

- **Chargement des données** : dans la vue `client_detail` (`core/views.py`), `client.payments.order_by("-paid_at").prefetch_related("allocations__sale")` — un seul aller-retour supplémentaire (paiements) plus un `prefetch_related` pour les imputations et leurs ventes liées, évitant une requête par paiement ou par imputation.
- **Emplacement dans le template** : une nouvelle section "Historique des paiements" dans `_client_detail_fragment.html`, entre les sections existantes "Ventes à crédit" et le formulaire d'enregistrement de paiement — cohérent avec l'ordre de lecture naturel (dette en cours, historique, action).
- **Rendu HTMX** : réutilise le fragment déjà en place (`_client_detail_fragment.html`, swappé via `hx-target="#client-detail-container"`) plutôt que de créer un fragment dédié, puisque l'historique doit se rafraîchir automatiquement après chaque nouveau paiement sans logique supplémentaire.

## Risks / Trade-offs

- [Un client avec un historique de paiements très long alourdirait la page] → Accepté pour ce palier : pas de pagination, cohérent avec le volume attendu d'une boutique unique (même choix que pour la liste des ventes non soldées du tableau de bord).
