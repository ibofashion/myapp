# responsive-web-access Specification

## Purpose

Décrit l'exigence d'accès de base à l'application via un navigateur web standard, aussi bien depuis un téléphone mobile que depuis un ordinateur, sans installation d'application dédiée.

## Requirements

### Requirement: Accès via navigateur web standard
Le système SHALL être utilisable dans un navigateur web standard (mobile ou ordinateur) via une simple URL, sans installation d'application native ni plugin.

#### Scenario: Ouverture depuis un navigateur mobile
- **WHEN** un utilisateur ouvre l'URL de l'application dans le navigateur de son téléphone
- **THEN** l'application se charge et est utilisable sans installation supplémentaire

#### Scenario: Ouverture depuis un navigateur de bureau
- **WHEN** un utilisateur ouvre l'URL de l'application dans un navigateur d'ordinateur
- **THEN** l'application se charge et est utilisable sans installation supplémentaire

### Requirement: Mise en page adaptable aux petits écrans
Le système SHALL afficher chaque page fonctionnelle (accueil, liste des clients, création de client, création de vente, détail client avec paiements) de façon lisible et utilisable sur un viewport mobile, sans défilement horizontal ni contenu tronqué.

#### Scenario: Consultation d'une page sur viewport mobile
- **WHEN** une page fonctionnelle est affichée sur un viewport d'environ 390px de large
- **THEN** la navigation, les formulaires et les listes restent lisibles et utilisables sans défilement horizontal

### Requirement: Mise en page adaptée aux grands écrans
Le système SHALL afficher chaque page fonctionnelle de façon lisible sur un viewport de bureau, avec un contenu centré qui ne s'étire pas de manière excessive.

#### Scenario: Consultation d'une page sur viewport desktop
- **WHEN** une page fonctionnelle est affichée sur un viewport d'environ 1280px de large
- **THEN** le contenu principal reste centré et lisible, sans lignes de texte ou de formulaire excessivement étirées
