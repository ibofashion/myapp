## Purpose

Permet à un vendeur de corriger ou annuler ses propres ventes, et à un admin de le faire sur toutes les ventes de la boutique, avec un contrôle d'autorisation appliqué côté serveur et jamais contournable par un accès direct à l'URL.

## ADDED Requirements

### Requirement: Modification d'une vente par son vendeur ou un admin
Le système SHALL permettre au vendeur associé à une vente, ou à un utilisateur de rôle `admin`, de modifier les lignes de cette vente (article, prix unitaire, quantité — ajout, suppression ou édition d'une ligne), en appliquant les mêmes règles de validation que la création d'une vente (au moins une ligne, prix unitaire ≥ 0, quantité > 0).

#### Scenario: Le vendeur d'origine modifie sa propre vente
- **WHEN** le vendeur qui a enregistré une vente modifie le prix unitaire d'une de ses lignes et soumet le formulaire
- **THEN** la vente est mise à jour avec le nouveau prix, et le total de la vente ainsi que son solde reflètent immédiatement ce changement

#### Scenario: Un admin modifie la vente d'un autre vendeur
- **WHEN** un utilisateur de rôle `admin` modifie une ligne d'une vente enregistrée par un autre vendeur
- **THEN** la modification est acceptée et enregistrée

#### Scenario: Modification vidant toutes les lignes refusée
- **WHEN** un utilisateur autorisé soumet une modification qui supprime toutes les lignes de la vente
- **THEN** la modification est rejetée et un message indique qu'au moins une ligne est requise

### Requirement: Annulation (suppression) d'une vente par son vendeur ou un admin
Le système SHALL permettre au vendeur associé à une vente, ou à un utilisateur de rôle `admin`, d'annuler (supprimer définitivement) cette vente, sauf si des paiements y sont déjà imputés.

#### Scenario: Annulation d'une vente sans paiement imputé
- **WHEN** le vendeur d'origine (ou un admin) annule une vente qui n'a aucune imputation de paiement
- **THEN** la vente et ses lignes sont définitivement supprimées

#### Scenario: Annulation refusée si des paiements sont déjà imputés
- **WHEN** un utilisateur autorisé tente d'annuler une vente ayant au moins une imputation de paiement
- **THEN** l'annulation est refusée et un message indique de retirer d'abord ces imputations

### Requirement: Autorisation serveur unique pour modifier/annuler une vente
Le système SHALL refuser la modification ou l'annulation d'une vente à tout vendeur qui n'est ni le vendeur associé à cette vente ni un utilisateur de rôle `admin`, y compris en cas d'accès direct à l'URL de modification ou d'annulation, indépendamment de ce qui est affiché dans l'interface.

#### Scenario: Un vendeur tente de modifier la vente d'un autre vendeur
- **WHEN** un vendeur de rôle `vendeur` accède à l'URL de modification d'une vente enregistrée par un autre vendeur
- **THEN** l'accès est refusé (403) et aucune modification n'est appliquée

#### Scenario: Un vendeur tente d'annuler la vente d'un autre vendeur
- **WHEN** un vendeur de rôle `vendeur` accède à l'URL d'annulation d'une vente enregistrée par un autre vendeur
- **THEN** l'accès est refusé (403) et la vente n'est pas supprimée

#### Scenario: Actions non affichées à un vendeur non autorisé
- **WHEN** un vendeur de rôle `vendeur` consulte le détail d'une vente enregistrée par un autre vendeur
- **THEN** les actions « Modifier » et « Annuler » ne sont pas proposées dans l'interface, sans que cela remplace le contrôle serveur
