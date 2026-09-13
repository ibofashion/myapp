## Why

Le gestionnaire de boutique suit actuellement ses ventes à crédit dans l'app Notes de son téléphone, sans aucun calcul automatique de total ligne, total vente ou solde. Ce sont les deux premières briques du MVP (PRD §4) : sans fiche client et sans saisie de vente à crédit, aucune autre fonctionnalité (paiement, statut, liste des ventes) ne peut exister. Ce changement pose ces fondations.

## What Changes

- Ajout de la fiche client : création d'un client avec `phone` (clé unique, normalisé avant écriture) et `name` (texte descriptif, peut se répéter).
- Ajout de la saisie d'une vente à crédit : sélection/rattachement à un client, saisie d'une ou plusieurs lignes d'article (nom libre, prix unitaire négocié, quantité).
- Calcul automatique et non stocké en dur du total par ligne (`prix unitaire × quantité`) et du total de la vente (somme des lignes), affichés à la saisie et à la lecture.
- Aucune vérification de doublon téléphone au-delà de la contrainte d'unicité en base (pas de normalisation floue, pas de fusion) — conforme au PRD §2.3.
- Ce changement ne couvre pas encore les paiements, le solde restant ni le statut dérivé (`non_payé`/`partiel`/`soldé`) — ces éléments dépendent de la vue `v_sale_balances` et seront traités dans un changement ultérieur. Les montants sont donc pour l'instant seulement le total de la vente, sans solde.

## Capabilities

### New Capabilities
- `client-management`: création d'une fiche client (nom + téléphone comme clé unique), avec normalisation et validation du numéro de téléphone.
- `credit-sale-creation`: création d'une vente à crédit rattachée à un client, avec lignes d'articles à prix libre et calcul automatique des totaux (ligne et vente).

### Modified Capabilities
(aucune — premier changement, aucune spec existante à modifier)

## Impact

- Scaffolding initial du projet Django (aucun code applicatif n'existe encore dans le dépôt) : `manage.py`, `requirements.txt`, app `core` (ou équivalent) pour les modèles `Client`, `Sale`, `SaleLine`.
- Nouveau modèle `Client` (PostgreSQL, contrainte `unique` sur `phone`).
- Nouveaux modèles `Sale` et `SaleLine` (voir ARCHITECTURE.md §2), sans encore la vue `v_sale_balances` (traitée dans un changement ultérieur portant sur les paiements/soldes).
- Nouvelles vues HTMX pour le formulaire de création client et le formulaire de vente à lignes multiples (ajout/suppression dynamique de lignes côté client via Alpine.js).
- Aucune authentification requise à ce stade (MVP mono-utilisateur, PRD §4).
