## Why

Une vente enregistrée avec une erreur (mauvais article, mauvais prix, doublon) ne peut aujourd'hui ni être corrigée ni être annulée : il n'existe aucune vue de modification ou de suppression de vente. La V1 du PRD (§2.4, §4) exige qu'un vendeur puisse corriger/annuler ses propres ventes et qu'un admin puisse le faire sur toutes les ventes de la boutique, avec un contrôle appliqué côté serveur (ARCHITECTURE.md §5, `can_edit_sale`) et non par simple masquage de bouton.

## What Changes

- Ajoute une vue de modification d'une vente existante (ses lignes : article, prix unitaire, quantité — ajout/suppression/édition de lignes), avec les mêmes règles de validation que la création (au moins une ligne, prix ≥ 0, quantité > 0).
- Ajoute une action d'annulation (suppression définitive) d'une vente, bloquée si la vente a déjà des `PaymentAllocation` imputées dessus (ARCHITECTURE.md §4.2), avec message expliquant qu'il faut d'abord retirer ces imputations.
- Ajoute `core/authz.py` avec `can_edit_sale(user, sale)` (`role == "admin"` ou `sale.seller_id == user.id`), appelée par les deux vues ci-dessus — jamais dupliquée ailleurs.
- Affiche les actions « Modifier » / « Annuler » sur la fiche vente uniquement pour les utilisateurs autorisés (confort d'UI ; le contrôle réel reste serveur).
- Un accès direct (URL) à la modification/suppression par un vendeur non autorisé est refusé (403), y compris pour un vendeur qui n'est ni le vendeur d'origine ni admin.

La gestion des comptes vendeurs par l'admin (création/désactivation) est déjà couverte par Django Admin (`core/admin.py`, capability `vendeur-accounts`) et n'est pas reprise ici. La visibilité de toutes les ventes par tout vendeur est déjà couverte par la capability `vendeur-accounts` (§ "Visibilité de toutes les ventes de la boutique par tout vendeur") et n'est pas reprise ici non plus.

## Capabilities

### New Capabilities
- `sale-edit-authorization`: modification et annulation d'une vente existante, restreintes par une autorisation serveur unique (vendeur propriétaire ou admin).

### Modified Capabilities
(aucune — les capabilities existantes ne changent pas de comportement)

## Impact

- `core/authz.py` (nouveau) : fonction `can_edit_sale`.
- `core/views.py` : nouvelles vues `sale_edit` et `sale_delete` (ou équivalent), appliquant `can_edit_sale` en tête de vue.
- `core/forms.py` : réutilisation ou adaptation de `SaleForm`/`SaleLineFormSet` pour l'édition d'une vente existante.
- `config/urls.py` : nouvelles routes pour modifier/annuler une vente.
- Templates : ajout des actions « Modifier »/« Annuler » sur `core/sale_detail.html`, nouveau template de formulaire d'édition.
- Tests : `core/tests/test_sale_authorization.py` (ou similaire) couvrant les scénarios d'autorisation, `core/tests/` pour la modification et l'annulation.
