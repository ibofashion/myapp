# credit-sale-creation Specification

## Purpose

Permet d'enregistrer une vente à crédit pour un client, avec une ou plusieurs lignes d'articles à prix libre, et de calculer automatiquement le total par ligne et le total de la vente afin de remplacer les calculs manuels faits jusqu'ici dans l'app Notes.

## Requirements

### Requirement: System MUST Support Credit Sale Creation
The system SHALL allow creating a credit sale linked to an existing client, made of one or more article lines, each with a free-text label, a negotiated unit price, and a quantity.

Le système doit permettre de créer une vente à crédit rattachée à un client existant, composée d'une ou plusieurs lignes d'articles. Chaque ligne comporte un nom d'article en texte libre, un prix unitaire négocié et une quantité.

#### Scenario: Création réussie avec plusieurs lignes
- **WHEN** l'utilisateur sélectionne un client existant et soumet une vente avec deux lignes ou plus, chacune avec un nom d'article, un prix unitaire positif et une quantité positive
- **THEN** la vente est enregistrée avec toutes ses lignes, rattachée au client sélectionné

#### Scenario: Vente sans client refusée
- **WHEN** l'utilisateur soumet une vente sans avoir sélectionné de client
- **THEN** la création est rejetée et un message indique qu'un client est requis

#### Scenario: Vente sans aucune ligne refusée
- **WHEN** l'utilisateur soumet une vente sans aucune ligne d'article
- **THEN** la création est rejetée et un message indique qu'au moins une ligne est requise

#### Scenario: Ligne avec quantité ou prix invalide refusée
- **WHEN** l'utilisateur soumet une ligne avec une quantité inférieure ou égale à zéro, ou un prix unitaire négatif
- **THEN** la création de la vente est rejetée et un message identifie la ligne en erreur

### Requirement: System MUST Automatically Calculate Line Totals
The system SHALL compute and display each line's total as unit price times quantity, and MUST NOT persist this value independently of the price and quantity that produced it.

Le système doit calculer et afficher le total de chaque ligne comme le produit du prix unitaire par la quantité, sans jamais stocker cette valeur de façon indépendante du prix et de la quantité qui l'ont produite.

#### Scenario: Total de ligne affiché
- **WHEN** une ligne a un prix unitaire de 1 500 et une quantité de 3
- **THEN** le total affiché pour cette ligne est 4 500

### Requirement: System MUST Automatically Calculate Sale Totals
The system SHALL compute and display the sale total as the sum of all its line totals, recalculated on every read rather than persisted.

Le système doit calculer et afficher le total de la vente comme la somme des totaux de toutes ses lignes, recalculé à chaque consultation plutôt que stocké en dur.

#### Scenario: Total de vente affiché
- **WHEN** une vente comporte une ligne totalisant 4 500 et une autre totalisant 2 000
- **THEN** le total de la vente affiché est 6 500

### Requirement: System MUST Allow Freely Negotiated Prices Per Line
The system SHALL allow freely entering each line's unit price, without constraining it to a catalog or to a price previously used for the same article label.

Le système doit permettre de saisir librement le prix unitaire de chaque ligne, sans le contraindre à un catalogue ou à un prix précédemment utilisé pour le même nom d'article.

#### Scenario: Même article, prix différents sur deux ventes
- **WHEN** l'utilisateur crée une vente avec une ligne "Sac de riz" à 12 000, puis une autre vente ultérieure avec une ligne "Sac de riz" à 13 500
- **THEN** les deux ventes sont enregistrées chacune avec son propre prix, sans erreur ni avertissement de contradiction

### Requirement: System MUST Support Idempotent Sale Submission
The system SHALL avoid creating duplicate sales when the same form submission is sent more than once with the same idempotency key, e.g. due to a double-tap on a slow connection.

Le système doit éviter la création de ventes dupliquées lorsqu'une même soumission de formulaire est envoyée plusieurs fois avec la même clé d'idempotence, par exemple à cause d'un double-tap sur une connexion lente.

#### Scenario: Double soumission avec la même clé d'idempotence
- **WHEN** deux requêtes de création de vente arrivent avec la même clé d'idempotence générée côté client
- **THEN** une seule vente est effectivement créée, et la seconde requête renvoie le résultat de la première sans créer de doublon
