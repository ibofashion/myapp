## Why

Les fiches client et la saisie de vente à crédit existent déjà (`client-management`, `credit-sale-creation`), mais rien ne permet encore de voir combien un client doit sur chacune de ses ventes, ni d'enregistrer un paiement. Sans cela, le gestionnaire de boutique ne peut pas encore remplacer l'app Notes pour le suivi du remboursement, qui est la moitié du problème initial (PRD §1 et §4, MVP).

## What Changes

- Ajout d'une vue listant les ventes d'un client avec, pour chacune, son total, le montant déjà payé, son solde restant et son statut dérivé (`non_payé` / `partiel` / `soldé`), calculés via la vue SQL `v_sale_balances` (ARCHITECTURE.md §3) — jamais stockés en dur.
- Ajout de l'enregistrement d'un paiement : montant, client associé, et répartition manuelle du vendeur/admin sur une ou plusieurs ventes précises de ce client au moment de la saisie (pas de répartition automatique/FIFO).
- Application des invariants de l'imputation d'un paiement (ARCHITECTURE.md §4.1) dans une transaction verrouillant les ventes concernées : la somme des imputations d'un paiement égale son montant, aucune vente ne peut recevoir plus que son solde restant, chaque imputation est strictement positive, et toutes les ventes ciblées appartiennent bien au client du paiement.
- Idempotence de la saisie de paiement (même principe que la création de vente, ARCHITECTURE.md §6) pour éviter un double paiement sur un double-tap réseau.
- Ce changement ne couvre pas la suppression d'une vente ni la ré-imputation/suppression d'une allocation existante (ARCHITECTURE.md §4.2) — hors périmètre, traité dans un changement ultérieur si besoin.

## Capabilities

### New Capabilities
- `sale-balance-tracking`: affichage, pour chaque vente d'un client, de son solde restant et de son statut dérivé automatiquement (non payé / partiel / soldé), à partir de la vue `v_sale_balances`.
- `payment-recording`: enregistrement d'un paiement pour un client et imputation manuelle de ce paiement sur une ou plusieurs de ses ventes, avec les invariants de non-dépassement et de répartition intégrale.

### Modified Capabilities
(aucune — les capacités existantes `client-management` et `credit-sale-creation` ne changent pas de comportement)

## Impact

- Nouveaux modèles `Payment` et `PaymentAllocation` (ARCHITECTURE.md §2), avec contrainte `CHECK (amount > 0)` sur `PaymentAllocation`.
- Nouvelle vue SQL `v_sale_balances` créée par migration (`migrations.RunSQL`) et modèle non managé `SaleBalance` associé (ARCHITECTURE.md §3).
- Nouvelle fonction métier `record_payment()` exécutée dans `transaction.atomic()` avec `select_for_update()` sur les ventes ciblées (ARCHITECTURE.md §4.1).
- Nouvelles vues HTMX : liste des ventes d'un client avec solde/statut, et formulaire de saisie de paiement avec sélection des ventes à imputer.
- Aucune authentification requise à ce stade (MVP mono-utilisateur, PRD §4) : pas de vérification de rôle/vendeur sur ces opérations pour l'instant.
