## Why

Le tableau de bord V1 (`dashboard`) donne une dette globale et une dette par client, mais un admin ne peut pas voir quel vendeur porte quel volume de dette en cours, ni retrouver rapidement les ventes non soldées les plus anciennes ou les plus importantes sans ouvrir chaque fiche client. Le palier V2 du PRD (§4) demande cet enrichissement pour aider au pilotage quotidien de la boutique.

## What Changes

- Ajout sur le tableau de bord d'une répartition de la dette en cours **par vendeur** (somme des soldes restants des ventes non soldées, groupées par vendeur ayant enregistré la vente), en plus de la dette globale et par client déjà existantes.
- Ajout d'une **liste des ventes non soldées** (statut `non payé` ou `partiel`) sur le tableau de bord, triable par colonne : date de vente, client, vendeur, montant du solde restant.
- Aucun changement de modèle de données : les deux enrichissements sont dérivés en lecture depuis `v_sale_balances` (et le vendeur associé à chaque vente), conformément à la règle établie qu'aucun total dérivé n'est stocké en dur.

## Capabilities

### New Capabilities
(aucune)

### Modified Capabilities
- `dashboard`: ajoute la répartition de la dette en cours par vendeur et la liste triable des ventes non soldées.

## Impact

- Vue tableau de bord existante (`core/views` dashboard) et son template : nouvelles sections à ajouter, sans toucher aux sections V1 existantes.
- Requêtes d'agrégation supplémentaires sur `v_sale_balances` jointes au vendeur de la vente ; pas de nouvelle table ni de nouveau champ stocké.
- Aucun impact sur l'autorisation : le tableau de bord reste accessible à tout utilisateur authentifié, vendeur ou admin (cf. `dashboard` §"Tableau de bord accessible à tout utilisateur authentifié").
