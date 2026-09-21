## ADDED Requirements

### Requirement: Création d'un compte vendeur par l'admin
Le système SHALL permettre à un utilisateur de rôle `admin` de créer un nouveau compte vendeur en fournissant un identifiant, un mot de passe et un rôle (`admin` ou `vendeur`).

#### Scenario: Création réussie d'un compte vendeur
- **WHEN** un admin soumet le formulaire de création de compte avec un identifiant unique, un mot de passe et un rôle
- **THEN** un nouveau compte est créé avec ce rôle, et ce compte peut immédiatement être utilisé pour se connecter

#### Scenario: Identifiant déjà utilisé refusé
- **WHEN** un admin soumet le formulaire de création de compte avec un identifiant déjà associé à un compte existant
- **THEN** la création est rejetée et un message indique que l'identifiant est déjà pris

### Requirement: Liste des comptes vendeurs consultable par l'admin
Le système SHALL permettre à un utilisateur de rôle `admin` de consulter la liste de tous les comptes vendeurs de la boutique avec leur identifiant et leur rôle.

#### Scenario: Consultation de la liste des comptes
- **WHEN** un admin ouvre la page de gestion des comptes vendeurs
- **THEN** tous les comptes existants s'affichent avec leur identifiant et leur rôle actuel

### Requirement: Modification du rôle d'un compte par l'admin
Le système SHALL permettre à un utilisateur de rôle `admin` de modifier le rôle (`admin` ↔ `vendeur`) d'un compte vendeur existant.

#### Scenario: Promotion d'un vendeur en admin
- **WHEN** un admin change le rôle d'un compte de `vendeur` à `admin` et confirme
- **THEN** ce compte dispose immédiatement des droits admin (modification/annulation de toutes les ventes, gestion des comptes)

#### Scenario: Rétrogradation d'un admin en vendeur
- **WHEN** un admin change le rôle d'un compte de `admin` à `vendeur` et confirme
- **THEN** ce compte perd immédiatement les droits admin et ne peut plus agir que sur ses propres ventes

### Requirement: Gestion des comptes réservée aux admins
Le système SHALL refuser l'accès aux pages et actions de gestion des comptes vendeurs (liste, création, modification de rôle) à tout utilisateur qui n'est pas de rôle `admin`, y compris en cas d'accès direct à l'URL.

#### Scenario: Un vendeur simple tente d'accéder à la gestion des comptes
- **WHEN** un utilisateur de rôle `vendeur` accède à l'URL de la page de gestion des comptes vendeurs
- **THEN** l'accès est refusé (403) et aucune information de compte n'est affichée

#### Scenario: Un vendeur simple tente de créer un compte par accès direct
- **WHEN** un utilisateur de rôle `vendeur` soumet directement une requête de création de compte vendeur
- **THEN** la création est refusée (403) et aucun compte n'est créé
