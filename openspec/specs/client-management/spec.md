# client-management Specification

## Purpose

Permet au gestionnaire de boutique de créer une fiche client identifiée de façon unique par son numéro de téléphone, remplaçant la liste de clients dispersée dans l'app Notes.

## Requirements

### Requirement: System MUST Support Client Record Creation
The system SHALL allow creating a client record from a name and a phone number, using the phone number as the unique key.

Le système doit permettre de créer une fiche client à partir d'un numéro de téléphone et d'un nom. Le numéro de téléphone est la clé unique du client ; le nom est une information descriptive qui peut se répéter entre plusieurs fiches.

#### Scenario: Création réussie
- **WHEN** l'utilisateur soumet un nom et un numéro de téléphone valides et non encore utilisés
- **THEN** une nouvelle fiche client est créée et devient sélectionnable pour l'enregistrement de ventes

#### Scenario: Numéro de téléphone obligatoire
- **WHEN** l'utilisateur soumet le formulaire sans numéro de téléphone
- **THEN** la création est rejetée et un message indique que le téléphone est requis

#### Scenario: Deux clients homonymes avec des numéros différents
- **WHEN** l'utilisateur crée un client dont le nom correspond exactement à celui d'un client existant, mais avec un numéro de téléphone différent
- **THEN** une fiche client distincte est créée, sans fusion ni avertissement de doublon de nom

### Requirement: System MUST Enforce Phone Number Uniqueness
The system SHALL reject creating a client record whose normalized phone number matches an existing client record.

Le système doit refuser la création d'une fiche client dont le numéro de téléphone, une fois normalisé, correspond à celui d'une fiche existante.

#### Scenario: Doublon exact rejeté
- **WHEN** l'utilisateur soumet un numéro de téléphone identique (après normalisation) à celui d'une fiche client existante
- **THEN** la création est rejetée et un message indique qu'un client avec ce numéro existe déjà

### Requirement: System MUST Normalize Phone Numbers Before Storage
The system SHALL normalize the phone number to a consistent format before any uniqueness check or persistence.

Le système doit normaliser le numéro de téléphone selon un format cohérent avant toute vérification d'unicité ou tout enregistrement en base.

#### Scenario: Formats équivalents reconnus comme identiques
- **WHEN** l'utilisateur saisit un numéro de téléphone déjà enregistré mais formaté différemment (espaces, tirets, préfixe international)
- **THEN** le système le normalise avant comparaison et le traite comme un doublon du numéro existant
