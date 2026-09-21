# vendeur-accounts Specification

## Purpose

Permet à chaque vendeur de la boutique de disposer d'un compte individuel (identifiant/mot de passe) distingué par un rôle admin ou vendeur simple, et garantit que tout vendeur connecté voit l'ensemble des ventes de la boutique.

## Requirements

### Requirement: Comptes vendeurs individuels avec rôle
Le système SHALL permettre à chaque vendeur de disposer d'un compte individuel identifié par un identifiant et un mot de passe, porteur d'un rôle parmi `admin` ou `vendeur`.

#### Scenario: Connexion avec un compte vendeur individuel
- **WHEN** un vendeur soumet son identifiant et son mot de passe valides sur l'écran de connexion
- **THEN** une session authentifiée est ouverte pour ce compte, avec son rôle (`admin` ou `vendeur`) associé

#### Scenario: Deux vendeurs, deux comptes distincts
- **WHEN** deux vendeurs différents de la boutique se connectent chacun avec leur propre identifiant
- **THEN** chaque session authentifiée correspond à son propre compte, sans partage d'identifiant entre eux

### Requirement: Connexion obligatoire pour accéder aux pages fonctionnelles
Le système SHALL exiger une session authentifiée pour accéder à toute page fonctionnelle (accueil, clients, ventes, paiements), et rediriger vers l'écran de connexion tout accès non authentifié.

#### Scenario: Accès direct sans session refusé
- **WHEN** un utilisateur non authentifié ouvre l'URL d'une page fonctionnelle de l'application
- **THEN** il est redirigé vers l'écran de connexion sans voir le contenu de la page demandée

#### Scenario: Accès après connexion
- **WHEN** un utilisateur s'authentifie avec succès
- **THEN** il accède aux pages fonctionnelles de l'application pour la durée de sa session

#### Scenario: Identifiants invalides refusés
- **WHEN** un utilisateur soumet un identifiant ou un mot de passe incorrect sur l'écran de connexion
- **THEN** la connexion est refusée et un message d'erreur s'affiche, sans ouverture de session

### Requirement: Déconnexion explicite
Le système SHALL permettre à un vendeur connecté de mettre fin à sa session à tout moment.

#### Scenario: Déconnexion réussie
- **WHEN** un vendeur connecté déclenche la déconnexion
- **THEN** sa session est terminée et il est redirigé vers l'écran de connexion

### Requirement: Attribution des nouvelles ventes et paiements au vendeur authentifié
Le système SHALL attribuer chaque nouvelle vente et chaque nouveau paiement au compte du vendeur authentifié qui effectue l'action, sans champ de sélection manuelle du vendeur dans le formulaire.

#### Scenario: Création d'une vente par un vendeur connecté
- **WHEN** un vendeur authentifié soumet le formulaire de création de vente
- **THEN** la vente est enregistrée avec ce vendeur comme vendeur associé, sans champ de sélection de vendeur dans le formulaire

#### Scenario: Enregistrement d'un paiement par un vendeur connecté
- **WHEN** un vendeur authentifié soumet le formulaire d'enregistrement d'un paiement
- **THEN** le paiement est enregistré avec ce vendeur comme auteur, sans champ de sélection de vendeur dans le formulaire

### Requirement: Visibilité de toutes les ventes de la boutique par tout vendeur
Le système SHALL permettre à tout vendeur authentifié, quel que soit son rôle, de consulter l'ensemble des ventes de la boutique et non uniquement celles qu'il a lui-même enregistrées.

#### Scenario: Un vendeur consulte une vente enregistrée par un autre vendeur
- **WHEN** un vendeur authentifié ouvre la fiche d'un client ou le détail d'une vente enregistrée par un autre vendeur
- **THEN** le contenu de la vente (lignes, total, solde, statut) s'affiche normalement, sans restriction liée au vendeur qui l'a enregistrée

#### Scenario: Liste des ventes d'un client non filtrée par vendeur connecté
- **WHEN** un vendeur authentifié consulte la liste des ventes d'un client
- **THEN** toutes les ventes de ce client apparaissent, y compris celles enregistrées par d'autres vendeurs

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
