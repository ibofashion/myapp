# last-price-suggestion Specification

## Purpose

Aide à la saisie d'une ligne de vente en rappelant au vendeur le dernier prix pratiqué pour un article donné, sans jamais imposer ni valider ce prix, puisqu'il n'existe pas de catalogue à prix fixe.

## Requirements

### Requirement: Suggestion du dernier prix pratiqué pour un article
Le système SHALL afficher, pendant la saisie du nom d'un article sur une ligne de vente, le dernier prix unitaire pratiqué pour un article portant exactement le même nom, si une telle ligne existe déjà dans une vente antérieure de la boutique, tous vendeurs confondus.

#### Scenario: Article déjà vendu précédemment
- **WHEN** le vendeur saisit un nom d'article qui correspond exactement au nom d'une ligne d'une vente antérieure de la boutique
- **THEN** le dernier prix unitaire pratiqué pour cet article (celui de la vente la plus récente portant ce nom) s'affiche comme suggestion

#### Scenario: Article jamais vendu
- **WHEN** le vendeur saisit un nom d'article qui ne correspond à aucune ligne de vente antérieure
- **THEN** aucune suggestion de prix ne s'affiche, et la saisie du prix reste libre

#### Scenario: Plusieurs prix historiques pour le même article
- **WHEN** un même nom d'article a été vendu à des prix différents lors de ventes antérieures
- **THEN** seul le prix de la vente la plus récente portant ce nom est suggéré

### Requirement: Suggestion strictement indicative
Le système SHALL permettre au vendeur de reprendre, modifier ou ignorer la suggestion de prix affichée, et ne SHALL NOT bloquer ni signaler comme erreur un prix saisi différent de la suggestion.

#### Scenario: Le vendeur ignore la suggestion
- **WHEN** une suggestion de prix s'affiche et que le vendeur saisit un prix différent
- **THEN** la ligne de vente est acceptée avec le prix saisi par le vendeur, sans avertissement ni blocage

#### Scenario: Le vendeur reprend la suggestion
- **WHEN** une suggestion de prix s'affiche et que le vendeur choisit de l'appliquer telle quelle au champ prix
- **THEN** le champ prix de la ligne est rempli avec la valeur suggérée, modifiable ensuite normalement
