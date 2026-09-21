# dashboard Specification

## Purpose

Donne à tout vendeur ou admin une vue d'ensemble immédiate de la dette en cours de la boutique (globale et par client) et des sommes encaissées récemment, sans avoir à parcourir chaque fiche client individuellement.

## Requirements

### Requirement: Dette totale en cours affichée globalement
Le système SHALL afficher sur le tableau de bord le total des dettes en cours de la boutique, calculé comme la somme des soldes restants de toutes les ventes non soldées, dérivé à la lecture à partir des soldes de vente courants.

#### Scenario: Dette globale avec plusieurs ventes non soldées
- **WHEN** un utilisateur authentifié ouvre le tableau de bord alors que la boutique a plusieurs ventes avec un solde restant supérieur à zéro
- **THEN** le total affiché est égal à la somme exacte de ces soldes restants

#### Scenario: Aucune dette en cours
- **WHEN** un utilisateur authentifié ouvre le tableau de bord alors que toutes les ventes de la boutique sont soldées
- **THEN** le total des dettes en cours affiché est 0

### Requirement: Dette en cours détaillée par client
Le système SHALL afficher sur le tableau de bord, pour chaque client ayant au moins une vente non soldée, le total de sa dette en cours (somme des soldes restants de ses ventes).

#### Scenario: Détail par client avec dettes multiples
- **WHEN** un utilisateur authentifié ouvre le tableau de bord alors que plusieurs clients ont chacun une dette en cours
- **THEN** chaque client concerné apparaît avec le total exact de sa dette en cours

#### Scenario: Client sans dette absent du détail
- **WHEN** un client a toutes ses ventes soldées
- **THEN** ce client n'apparaît pas dans le détail des dettes par client

### Requirement: Total encaissé sur une période présélectionnée
Le système SHALL afficher sur le tableau de bord le total des paiements enregistrés sur une période choisie parmi des présets (aujourd'hui, cette semaine, ce mois), la période par défaut étant « aujourd'hui ».

#### Scenario: Changement de préset de période
- **WHEN** un utilisateur authentifié sélectionne le préset « ce mois » sur le tableau de bord
- **THEN** le total affiché correspond à la somme des montants de tous les paiements dont la date se situe dans le mois en cours

#### Scenario: Aucun paiement sur la période
- **WHEN** un utilisateur authentifié consulte une période sur laquelle aucun paiement n'a été enregistré
- **THEN** le total encaissé affiché pour cette période est 0

### Requirement: Tableau de bord accessible à tout utilisateur authentifié
Le système SHALL rendre le tableau de bord accessible à tout utilisateur authentifié, vendeur ou admin, sans restriction liée au rôle, conformément à la visibilité partagée de l'ensemble des ventes de la boutique.

#### Scenario: Accès par un vendeur simple
- **WHEN** un utilisateur de rôle `vendeur` ouvre la page du tableau de bord
- **THEN** les mêmes totaux (dette globale, dette par client, encaissements par période) que ceux vus par un admin s'affichent

#### Scenario: Accès refusé sans authentification
- **WHEN** un utilisateur non authentifié tente d'ouvrir l'URL du tableau de bord
- **THEN** il est redirigé vers l'écran de connexion sans voir aucun montant
