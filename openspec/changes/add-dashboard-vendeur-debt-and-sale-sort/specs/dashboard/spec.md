## ADDED Requirements

### Requirement: Dette en cours détaillée par vendeur
Le système SHALL afficher sur le tableau de bord, pour chaque vendeur ayant enregistré au moins une vente non soldée, le total de la dette en cours portée par ses ventes (somme des soldes restants des ventes qu'il a enregistrées et qui ne sont pas encore soldées).

#### Scenario: Répartition par vendeur avec plusieurs vendeurs actifs
- **WHEN** un utilisateur authentifié ouvre le tableau de bord alors que plusieurs vendeurs ont chacun enregistré des ventes non soldées
- **THEN** chaque vendeur concerné apparaît avec le total exact des soldes restants des ventes qu'il a enregistrées

#### Scenario: Vendeur sans vente non soldée absent de la répartition
- **WHEN** un vendeur n'a enregistré aucune vente, ou seulement des ventes déjà soldées
- **THEN** ce vendeur n'apparaît pas dans la répartition de la dette par vendeur

#### Scenario: Somme des dettes par vendeur cohérente avec la dette globale
- **WHEN** un utilisateur authentifié consulte la répartition par vendeur
- **THEN** la somme des totaux affichés pour chaque vendeur est égale au total de la dette globale en cours affiché par ailleurs sur le tableau de bord

### Requirement: Liste triable des ventes non soldées
Le système SHALL afficher sur le tableau de bord une liste des ventes ayant le statut `non payé` ou `partiel`, incluant pour chacune la date de vente, le client, le vendeur et le solde restant, et SHALL permettre de trier cette liste par date de vente, par montant de solde restant, par client ou par vendeur.

#### Scenario: Liste initiale des ventes non soldées
- **WHEN** un utilisateur authentifié ouvre le tableau de bord alors que la boutique a des ventes non payées ou partiellement payées
- **THEN** chacune de ces ventes apparaît dans la liste avec sa date, son client, son vendeur et son solde restant, et aucune vente soldée n'y apparaît

#### Scenario: Tri par solde restant décroissant
- **WHEN** un utilisateur authentifié choisit de trier la liste des ventes non soldées par solde restant décroissant
- **THEN** les ventes s'affichent dans l'ordre décroissant de leur solde restant

#### Scenario: Tri par date de vente
- **WHEN** un utilisateur authentifié choisit de trier la liste des ventes non soldées par date de vente
- **THEN** les ventes s'affichent dans l'ordre chronologique demandé (croissant ou décroissant selon le sens choisi)

#### Scenario: Aucune vente non soldée
- **WHEN** un utilisateur authentifié ouvre le tableau de bord alors que toutes les ventes de la boutique sont soldées
- **THEN** la liste des ventes non soldées s'affiche vide, sans erreur
