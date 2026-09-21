## Why

Le PRD (§4, palier V1) demande un tableau de bord basique donnant une vue d'ensemble de la santé financière de la boutique — dette en cours et encaissements — sans avoir à ouvrir chaque fiche client une par une. Aujourd'hui, connaître la dette totale ou l'encaissement récent nécessite de parcourir les clients un à un.

## What Changes

- Ajout d'une page « Tableau de bord » accessible à tout utilisateur authentifié (vendeur ou admin), affichant :
  - le total des dettes en cours, toutes ventes non soldées confondues (global boutique) ;
  - le détail du total dû par client, pour les clients ayant une dette en cours ;
  - le total encaissé sur une période sélectionnée parmi des présets simples (aujourd'hui / cette semaine / ce mois).
- Tous les montants du tableau de bord sont calculés à la lecture à partir de `v_sale_balances`/`SaleBalance` et des paiements enregistrés — aucun total n'est stocké en dur.

## Capabilities

### New Capabilities
- `dashboard`: vue d'ensemble des dettes en cours (globale et par client) et des encaissements sur une période, pour tout vendeur ou admin authentifié.

### Modified Capabilities
(aucune)

## Impact

- `core/views.py`, `core/urls.py`, `templates/`: nouvelle vue et template de tableau de bord.
- Lecture agrégée sur `SaleBalance` (dette en cours) et sur le modèle `Payment` (encaissements par période) — aucun nouveau champ stocké, aucune migration de données.
- Navigation : nouveau lien « Tableau de bord » pour tout utilisateur connecté.
