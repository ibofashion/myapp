## Why

Le MVP fonctionne avec un unique compte vendeur "bootstrap" attribué automatiquement, sans écran de connexion. Pour que la boutique puisse être utilisée par toute l'équipe (PRD §4, palier V1), chaque vendeur a besoin de son propre compte, et le système doit distinguer un rôle admin d'un rôle vendeur simple. C'est le socle qui rend l'application déployable à plusieurs personnes.

Ce change couvre strictement les trois premiers points de la V1 (PRD §2.4 et §4) : comptes vendeurs individuels, rôles admin/vendeur, et visibilité de toutes les ventes par chaque vendeur. Les permissions de modification/annulation de vente (`can_edit_sale`) et le tableau de bord basique restent hors périmètre de ce change et seront traités séparément.

## What Changes

- Ajout d'un champ `role` (`admin` / `vendeur`) sur le modèle utilisateur existant (`User`, déjà prévu par ARCHITECTURE.md §2).
- Ajout d'un écran de connexion (identifiant/mot de passe) et de déconnexion ; toutes les pages fonctionnelles nécessitent désormais une session authentifiée. **BREAKING** : les pages fonctionnelles ne sont plus accessibles sans connexion (le MVP les rendait accessibles sans authentification).
- Les comptes vendeurs individuels sont créés via l'interface Django Admin (déjà prévue pour cet usage par ARCHITECTURE.md §1) — aucune interface de gestion de compte dédiée n'est construite dans ce change.
- Les nouvelles ventes et les nouveaux paiements sont désormais attribués au vendeur authentifié (`request.user`) qui effectue l'action, et non plus au compte vendeur bootstrap unique du MVP.
- Suppression du mécanisme de création automatique du compte vendeur bootstrap et de la dispense d'authentification du MVP.
- Confirmation que tout vendeur ou admin authentifié voit l'ensemble des ventes de la boutique (fiche client, détail de vente) — aucun filtrage par vendeur connecté n'est appliqué à la consultation.

## Capabilities

### New Capabilities
- `vendeur-accounts`: comptes vendeurs individuels avec identifiant/mot de passe, rôle (`admin` ou `vendeur`), connexion/déconnexion obligatoires pour accéder aux pages fonctionnelles, et attribution des nouvelles ventes/paiements au vendeur authentifié. Couvre aussi la règle selon laquelle tout vendeur connecté voit l'intégralité des ventes de la boutique, sans filtrage par vendeur.

### Modified Capabilities
- `single-user-access`: les exigences du MVP (accès sans authentification, attribution automatique à un compte vendeur bootstrap unique) sont remplacées par l'obligation de connexion individuelle et l'attribution au vendeur réellement authentifié.

## Impact

- **Modèle** : ajout du champ `role` sur `User` (migration Django).
- **Vues** : `home`, `client_list`, `client_create`, `client_detail`, `sale_create`, `sale_detail` passent sous protection d'authentification (`login_required` ou équivalent) ; `sale_create` et l'enregistrement de paiement utilisent `request.user` comme vendeur/auteur au lieu du compte bootstrap.
- **URLs/templates** : ajout des routes et gabarits de connexion/déconnexion (`django.contrib.auth`).
- **Admin Django** : exposition du champ `role` dans l'admin pour la création des comptes vendeurs par l'admin.
- **Comptes existants** : le compte vendeur bootstrap du MVP et les ventes/paiements déjà enregistrés sous ce compte conservent leur attribution historique ; aucune migration de données n'est requise (hypothèse — aucune donnée de production MVP à reprendre, cf. PRD §2.5).
- **Hors périmètre de ce change** : permissions de modification/annulation de vente (`can_edit_sale`), gestion des comptes vendeurs via une interface applicative (reste dans Django Admin), tableau de bord.
