## Why

La V1 introduit les comptes vendeurs individuels et les rôles (`admin`/`vendeur`), mais rien ne permet aujourd'hui de créer ces comptes depuis l'application : ils n'existent que via des outils d'administration hors application (ex. `createsuperuser`/admin Django). L'admin a besoin de créer de nouveaux comptes vendeurs, de voir qui a un compte, et d'ajuster un rôle en cas d'erreur ou d'évolution d'équipe, sans quitter l'application.

## What Changes

- Ajout d'une page « Comptes vendeurs », accessible uniquement à l'admin, listant tous les comptes existants (identifiant, rôle).
- Ajout d'un formulaire admin de création de compte vendeur (identifiant + mot de passe + rôle).
- Ajout d'une action admin permettant de modifier le rôle (`admin` ↔ `vendeur`) d'un compte existant.
- Contrôle serveur systématique : ces pages/actions sont refusées (403) à tout utilisateur non-admin, y compris par accès direct à l'URL.

Hors périmètre de ce change (voir clarification avec le porteur de produit) : désactivation/suppression de compte, réinitialisation de mot de passe — non demandées pour l'instant.

## Capabilities

### New Capabilities
(aucune — ce change étend la capacité existante `vendeur-accounts`)

### Modified Capabilities
- `vendeur-accounts`: ajoute la gestion des comptes par l'admin (création, liste, modification du rôle), avec autorisation serveur réservant ces actions au rôle `admin`.

## Impact

- `core/models.py`: aucun changement de modèle attendu (le modèle `User` a déjà `role`).
- `core/views.py`, `core/urls.py`, `templates/`: nouvelles vues et templates pour la liste, la création et la modification de rôle des comptes vendeurs.
- `core/authz.py` ou équivalent: nouvelle vérification serveur réservant ces vues au rôle `admin`.
- Tests: nouveaux tests d'autorisation et de comportement (création, liste, changement de rôle, refus pour non-admin).
