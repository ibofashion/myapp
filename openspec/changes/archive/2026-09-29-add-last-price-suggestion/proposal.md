## Why

Lors de la saisie d'une ligne de vente, le vendeur doit se souvenir ou redemander au client le prix pratiqué la dernière fois pour un article donné, faute de catalogue à prix fixe. Le PRD (§4, palier V2) demande une aide à la saisie qui rappelle le dernier prix pratiqué pour un même nom d'article, sans jamais l'imposer.

## What Changes

- Ajout d'une suggestion du dernier prix pratiqué pour un article, affichée pendant la saisie d'une ligne de vente dès que le vendeur renseigne un nom d'article déjà utilisé dans une vente précédente (toutes ventes de la boutique, tous vendeurs confondus).
- La suggestion est calculée à la lecture via `DISTINCT ON (label) ... ORDER BY label, sold_at DESC` sur `SaleLine`, sans table ni champ dédié de mémorisation de prix.
- La suggestion reste purement indicative : le vendeur peut la reprendre, la modifier ou l'ignorer complètement ; elle ne contraint et ne valide en aucun cas le prix saisi.
- Aucun changement au comportement de `credit-sale-creation` : le prix négocié par ligne reste librement saisissable et n'est ni bloqué ni comparé au prix suggéré.

## Capabilities

### New Capabilities
- `last-price-suggestion`: suggestion en lecture seule du dernier prix pratiqué pour un article donné, affichée comme aide à la saisie sur le formulaire de création de vente.

### Modified Capabilities
(aucune — la saisie libre du prix par ligne, garantie par `credit-sale-creation`, n'est pas modifiée)

## Impact

- Formulaire/template de création de vente (`credit-sale-creation`) : ajout d'un appel HTMX déclenché à la saisie du nom d'article, sans changer la validation existante des lignes.
- Nouvelle requête de lecture sur `SaleLine` (via `DISTINCT ON (label)`), aucune migration de schéma requise.
- Aucun impact sur l'autorisation ou sur les autres capacités (paiements, tableau de bord, comptes vendeurs).
