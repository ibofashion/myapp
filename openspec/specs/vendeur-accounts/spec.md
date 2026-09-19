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
