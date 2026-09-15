# single-user-access Specification

## Purpose

Décrit le fonctionnement du MVP sans authentification multi-utilisateur : toutes les ventes et tous les paiements sont attribués automatiquement à un unique compte vendeur, sans écran de connexion ni gestion de plusieurs comptes.

## Requirements

### Requirement: Attribution automatique à un vendeur unique
Le système SHALL attribuer automatiquement chaque vente et chaque paiement enregistré à un unique compte vendeur bootstrap, sans demander à l'utilisateur de s'identifier ou de choisir un vendeur.

#### Scenario: Création d'une vente sans sélection de vendeur
- **WHEN** un utilisateur soumet le formulaire de création de vente
- **THEN** la vente est enregistrée avec le compte vendeur bootstrap comme vendeur, sans champ de sélection de vendeur dans le formulaire

#### Scenario: Enregistrement d'un paiement sans sélection de vendeur
- **WHEN** un utilisateur soumet le formulaire d'enregistrement d'un paiement
- **THEN** le paiement est enregistré avec le compte vendeur bootstrap comme auteur, sans champ de sélection de vendeur dans le formulaire

### Requirement: Aucune authentification requise en MVP
Le système SHALL permettre l'accès à toutes les pages fonctionnelles de l'application (accueil, clients, ventes, paiements) sans identifiant ni mot de passe.

#### Scenario: Accès direct aux pages fonctionnelles
- **WHEN** un utilisateur ouvre une URL de l'application (hors interface d'administration Django)
- **THEN** la page se charge et affiche son contenu sans redirection vers un écran de connexion

### Requirement: Compte vendeur bootstrap idempotent
Le système SHALL garantir qu'un unique compte vendeur bootstrap existe, en le créant automatiquement à la première utilisation s'il n'existe pas déjà, sans jamais en créer de doublon.

#### Scenario: Première opération sur une base vide
- **WHEN** aucune vente ni paiement n'a encore été enregistré et que le compte vendeur bootstrap n'existe pas
- **THEN** le système crée ce compte avec un mot de passe inutilisable (connexion impossible) avant d'enregistrer l'opération en cours

#### Scenario: Opérations suivantes
- **WHEN** le compte vendeur bootstrap existe déjà et qu'une nouvelle vente ou un nouveau paiement est enregistré
- **THEN** le système réutilise le compte existant sans en créer un second
