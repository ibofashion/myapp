# sale-balance-tracking Specification

## Purpose

Permet de savoir, pour chaque vente à crédit d'un client, combien il reste à payer et où en est le remboursement, en calculant systématiquement le solde et le statut à la lecture plutôt qu'en les stockant en dur.

## Requirements

### Requirement: System MUST List a Client's Sales With Their Remaining Balance
The system SHALL display, for a given client, the list of their credit sales, each showing its total, amount already paid, and remaining balance.

Le système doit afficher, pour un client donné, la liste de ses ventes à crédit, chacune avec son total, le montant déjà payé, et le solde restant.

#### Scenario: Liste affichée pour un client avec plusieurs ventes
- **WHEN** l'utilisateur consulte la fiche d'un client ayant deux ventes à crédit ou plus
- **THEN** chaque vente apparaît dans la liste avec son total, son montant payé et son solde restant

#### Scenario: Client sans aucune vente
- **WHEN** l'utilisateur consulte la fiche d'un client n'ayant aucune vente à crédit
- **THEN** la liste des ventes est vide et un message indique l'absence de vente

### Requirement: System MUST Derive Sale Status Automatically
The system SHALL derive each sale's status as "non payé" when nothing has been paid, "soldé" when the amount paid covers the full total, and "partiel" otherwise, computed from current totals and allocations rather than stored independently.

Le système doit dériver le statut de chaque vente : "non payé" quand rien n'a encore été payé, "soldé" quand le montant payé couvre l'intégralité du total, et "partiel" dans les autres cas, calculé à partir des totaux et imputations actuels plutôt que stocké indépendamment.

#### Scenario: Vente sans aucun paiement imputé
- **WHEN** une vente n'a reçu aucune imputation de paiement
- **THEN** son statut affiché est "non payé" et son solde restant est égal à son total

#### Scenario: Vente partiellement payée
- **WHEN** une vente de total 10 000 a reçu 4 000 d'imputations
- **THEN** son solde restant affiché est 6 000 et son statut est "partiel"

#### Scenario: Vente intégralement soldée
- **WHEN** une vente de total 10 000 a reçu 10 000 d'imputations cumulées
- **THEN** son solde restant affiché est 0 et son statut est "soldé"

### Requirement: System MUST Recompute Balance and Status Without Persisting Them Independently
The system SHALL recompute each sale's balance and status on every read from the sale's lines and payment allocations, and MUST NOT persist balance or status as fields updated by application code.

Le système doit recalculer le solde et le statut de chaque vente à chaque consultation, à partir des lignes de la vente et des imputations de paiement, et ne doit pas stocker le solde ou le statut comme des champs mis à jour par le code applicatif.

#### Scenario: Solde à jour immédiatement après une imputation
- **WHEN** un paiement vient d'être imputé sur une vente
- **THEN** le solde restant et le statut affichés pour cette vente reflètent immédiatement cette imputation, sans étape de recalcul manuelle
