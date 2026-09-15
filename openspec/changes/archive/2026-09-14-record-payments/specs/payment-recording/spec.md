## Purpose

Permet d'enregistrer un paiement reçu d'un client et de l'imputer manuellement sur une ou plusieurs de ses ventes à crédit, afin que chaque vente conserve son propre solde et son propre statut sans répartition automatique.

## ADDED Requirements

### Requirement: System MUST Support Recording a Payment Against a Client
The system SHALL allow recording a payment with an amount and a date, associated with a client rather than directly with a single sale.

Le système doit permettre d'enregistrer un paiement avec un montant et une date, rattaché à un client plutôt que directement à une seule vente.

#### Scenario: Paiement enregistré pour un client
- **WHEN** l'utilisateur saisit un montant positif pour un client existant
- **THEN** un paiement est créé pour ce client avec ce montant

#### Scenario: Paiement avec montant nul ou négatif refusé
- **WHEN** l'utilisateur soumet un paiement avec un montant inférieur ou égal à zéro
- **THEN** l'enregistrement est rejeté et un message indique que le montant doit être positif

### Requirement: System MUST Support Manual Allocation of a Payment Across Sales
The system SHALL let the user choose, at entry time, which one or more of the client's sales receive which portion of the payment amount, without applying any automatic or FIFO allocation.

Le système doit permettre à l'utilisateur de choisir, au moment de la saisie, sur laquelle ou lesquelles des ventes du client le montant du paiement est réparti, sans appliquer de répartition automatique ou FIFO.

#### Scenario: Imputation sur une seule vente
- **WHEN** l'utilisateur enregistre un paiement de 5 000 et l'impute intégralement sur une vente du client ayant un solde restant d'au moins 5 000
- **THEN** le solde restant de cette vente diminue de 5 000

#### Scenario: Imputation répartie sur plusieurs ventes
- **WHEN** l'utilisateur enregistre un paiement de 7 000 et l'impute pour 3 000 sur une vente et 4 000 sur une autre vente du même client
- **THEN** chacune des deux ventes voit son solde restant diminuer du montant qui lui a été imputé

### Requirement: System MUST Fully Allocate Every Payment
The system SHALL require that the sum of a payment's allocations equals the payment's total amount before the payment is committed.

Le système doit exiger que la somme des imputations d'un paiement soit égale au montant total du paiement avant que l'enregistrement ne soit validé.

#### Scenario: Répartition incomplète refusée
- **WHEN** l'utilisateur enregistre un paiement de 10 000 mais n'impute au total que 6 000 sur les ventes sélectionnées
- **THEN** l'enregistrement est rejeté et un message indique que le montant réparti ne correspond pas au montant du paiement

#### Scenario: Répartition excédentaire refusée
- **WHEN** l'utilisateur tente d'imputer un total supérieur au montant du paiement sur les ventes sélectionnées
- **THEN** l'enregistrement est rejeté et un message indique que le montant réparti dépasse le montant du paiement

### Requirement: System MUST Prevent Over-Allocating a Sale
The system SHALL reject any allocation, or combination of allocations, that would cause the sum of a sale's allocations to exceed that sale's total.

Le système doit refuser toute imputation, ou combinaison d'imputations, qui ferait dépasser à une vente la somme de son total par les imputations qu'elle a reçues.

#### Scenario: Imputation dépassant le solde restant d'une vente
- **WHEN** l'utilisateur tente d'imputer sur une vente un montant supérieur à son solde restant actuel
- **THEN** l'enregistrement est rejeté et un message indique que ce montant dépasse le solde restant de la vente

### Requirement: System MUST Reject Non-Positive Allocation Amounts
The system SHALL require every individual allocation amount to be strictly greater than zero.

Le système doit exiger que chaque montant d'imputation individuel soit strictement supérieur à zéro.

#### Scenario: Imputation nulle refusée
- **WHEN** l'utilisateur tente d'imputer un montant de zéro sur une vente sélectionnée
- **THEN** l'enregistrement est rejeté et un message indique qu'une imputation doit être strictement positive

### Requirement: System MUST Restrict Allocations to the Payment's Own Client
The system SHALL only allow a payment's allocations to target sales belonging to the same client as the payment.

Le système doit uniquement permettre aux imputations d'un paiement de cibler des ventes appartenant au même client que le paiement.

#### Scenario: Tentative d'imputation sur la vente d'un autre client refusée
- **WHEN** l'utilisateur tente d'imputer un paiement sur une vente qui n'appartient pas au client de ce paiement
- **THEN** l'enregistrement est rejeté et un message indique que la vente n'appartient pas à ce client

### Requirement: System MUST Record Payments Idempotently
The system SHALL avoid creating a duplicate payment when the same payment submission is sent more than once with the same client-generated idempotency key.

Le système doit éviter de créer un paiement en double lorsqu'une même soumission de paiement est envoyée plusieurs fois avec la même clé d'idempotence générée côté client.

#### Scenario: Double soumission d'un paiement avec la même clé d'idempotence
- **WHEN** deux requêtes d'enregistrement de paiement arrivent avec la même clé d'idempotence
- **THEN** un seul paiement est effectivement créé et enregistré, la seconde requête ne crée pas de doublon
