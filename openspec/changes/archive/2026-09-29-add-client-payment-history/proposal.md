## Why

Le modèle de données enregistre déjà chaque paiement et ses imputations (`Payment`, `PaymentAllocation`), mais aucune vue ne les affiche : après l'enregistrement d'un paiement, il redevient invisible. Un utilisateur qui teste l'app l'a remarqué en conditions réelles — il n'a aucun moyen de vérifier a posteriori qui a payé quoi, quand, et sur quelle vente, ce qui rend le suivi du recouvrement de crédit opaque.

## What Changes

- Sur la fiche client (`core/client_detail.html` / `_client_detail_fragment.html`), ajouter une section "Historique des paiements" listant tous les paiements déjà reçus de ce client, du plus récent au plus ancien.
- Pour chaque paiement affiché : la date (`paid_at`), le montant reçu (`amount`), et le détail de ses imputations (`PaymentAllocation`) — numéro de vente (lien vers `sale_detail`) et montant imputé pour chacune.
- Alimenter cette section depuis la vue `client_detail` (`core/views.py`) en chargeant les paiements du client avec leurs imputations et ventes liées (`select_related`/`prefetch_related`), sans dupliquer ni recalculer aucune valeur financière déjà stockée.
- Portée strictement en lecture seule : pas d'édition ni de suppression de paiement, et pas d'affichage équivalent sur la fiche vente (décision de périmètre validée avec l'utilisateur).

## Capabilities

### New Capabilities
- `payment-history`: affichage en lecture seule, sur la fiche client, de l'historique des paiements reçus et de leurs imputations par vente.

### Modified Capabilities
(aucune — le comportement d'enregistrement des paiements ne change pas)

## Impact

- `core/views.py` : `client_detail` — charger les paiements du client (avec `allocations__sale`) et les passer au contexte.
- `templates/core/_client_detail_fragment.html` : nouvelle section de liste des paiements.
- `core/tests/` : nouveau test couvrant l'affichage de l'historique (paiement avec imputation simple et imputation répartie sur plusieurs ventes).
- Aucun changement de schéma de base de données, aucune nouvelle dépendance.
