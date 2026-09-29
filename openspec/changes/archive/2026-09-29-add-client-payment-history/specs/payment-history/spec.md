## Purpose

Donne à l'utilisateur une vue en lecture seule, sur la fiche client, de tous les paiements déjà reçus de ce client et de la manière dont chacun a été imputé sur ses ventes, pour un suivi fiable du recouvrement de crédit.

## ADDED Requirements

### Requirement: System MUST Display a Client's Payment History
The system SHALL display, on a client's detail page, the list of all payments already recorded for that client, ordered from most recent to oldest.

Le système doit afficher, sur la fiche d'un client, la liste de tous les paiements déjà enregistrés pour ce client, triée du plus récent au plus ancien.

#### Scenario: Client avec plusieurs paiements enregistrés
- **WHEN** l'utilisateur consulte la fiche d'un client ayant déjà reçu deux paiements à des dates différentes
- **THEN** les deux paiements apparaissent dans l'historique, le plus récent en premier

#### Scenario: Client sans aucun paiement enregistré
- **WHEN** l'utilisateur consulte la fiche d'un client n'ayant encore reçu aucun paiement
- **THEN** l'historique affiche un message indiquant qu'aucun paiement n'a encore été enregistré

### Requirement: System MUST Show Each Payment's Date and Amount
The system SHALL show, for each payment in the history, its recorded date and the amount received.

Le système doit afficher, pour chaque paiement de l'historique, sa date d'enregistrement et le montant reçu.

#### Scenario: Détail d'un paiement affiché
- **WHEN** l'utilisateur consulte l'historique des paiements d'un client
- **THEN** chaque paiement affiché indique sa date et son montant

### Requirement: System MUST Show Each Payment's Allocation Breakdown
The system SHALL show, for each payment in the history, the breakdown of its allocations across the client's sales, including the sale number and the amount allocated to that sale, with a link to the corresponding sale's detail page.

Le système doit afficher, pour chaque paiement de l'historique, le détail de ses imputations sur les ventes du client, en indiquant le numéro de la vente et le montant qui lui a été imputé, avec un lien vers la fiche de cette vente.

#### Scenario: Paiement imputé sur une seule vente
- **WHEN** un paiement a été intégralement imputé sur une seule vente du client
- **THEN** l'historique affiche cette vente et le montant qui lui a été imputé, avec un lien vers sa fiche

#### Scenario: Paiement réparti sur plusieurs ventes
- **WHEN** un paiement a été imputé sur plusieurs ventes du client
- **THEN** l'historique affiche chacune des ventes concernées avec le montant qui lui a été imputé respectivement
