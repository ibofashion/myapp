## REMOVED Requirements

### Requirement: Attribution automatique à un vendeur unique
**Reason**: La V1 introduit des comptes vendeurs individuels ; chaque vente et chaque paiement sont désormais attribués au vendeur réellement authentifié, et non plus à un unique compte bootstrap partagé.
**Migration**: Voir la capacité `vendeur-accounts`, exigence "Attribution des nouvelles ventes et paiements au vendeur authentifié".

### Requirement: Aucune authentification requise en MVP
**Reason**: La V1 exige une session authentifiée pour accéder aux pages fonctionnelles ; l'accès libre sans identifiant/mot de passe du MVP n'est plus valable.
**Migration**: Voir la capacité `vendeur-accounts`, exigence "Connexion obligatoire pour accéder aux pages fonctionnelles".

### Requirement: Compte vendeur bootstrap idempotent
**Reason**: Le compte vendeur bootstrap unique du MVP est remplacé par des comptes vendeurs individuels créés via Django Admin ; il n'y a plus de création automatique d'un compte partagé.
**Migration**: Les comptes vendeurs sont désormais créés manuellement par l'admin dans Django Admin. Le compte bootstrap existant et les ventes/paiements déjà enregistrés sous ce compte conservent leur attribution historique sans migration de données.
