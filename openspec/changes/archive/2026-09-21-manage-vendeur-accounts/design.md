## Context

Le modèle `User` (`core/models.py`) hérite déjà de `AbstractUser` et porte un champ `role` (`admin`/`vendeur`). L'autorisation existante centralise les vérifications d'accès dans `core/authz.py` (ex. `can_edit_sale`). Voir proposal.md - Why pour la motivation.

## Goals / Non-Goals

**Goals:**
- Permettre à un admin de créer, lister et changer le rôle d'un compte vendeur depuis l'application.
- Garder l'autorisation serveur centralisée et testable, dans le même esprit que `can_edit_sale`.

**Non-Goals:**
- Désactivation, suppression ou réinitialisation de mot de passe d'un compte (non demandées à ce stade).
- Auto-inscription ou gestion de profil par le vendeur lui-même.

## Decisions

- **Vérification d'autorisation** : ajouter une fonction dédiée `is_admin(user)` dans `core/authz.py`, aux côtés de `can_edit_sale`, plutôt que de dupliquer `user.role == "admin"` dans chaque vue. Chaque vue de gestion des comptes l'appelle en tout début de traitement et renvoie 403 si elle échoue.
- **Formulaires** : utiliser un `ModelForm` Django standard sur `User` (identifiant, mot de passe, rôle) plutôt qu'un formulaire manuel, pour bénéficier de la validation de mot de passe intégrée à Django.
- **Changement de rôle** : action distincte de l'édition générale du compte (pas de formulaire d'édition complet du profil), pour rester strictement dans le périmètre demandé (liste, création, rôle).

## Risks / Trade-offs

- [Un admin se rétrograde lui-même par erreur et perd l'accès à la gestion des comptes] → Autoriser l'action (pas de garde-fou spécial demandé) ; un autre admin ou un accès à l'admin Django reste disponible en secours.
- [Pas de suppression/désactivation prévue dans ce change] → Un compte créé par erreur ne peut être neutralisé que par changement de rôle vers `vendeur`, ou via l'admin Django ; acceptable car hors périmètre confirmé avec le porteur de produit.
