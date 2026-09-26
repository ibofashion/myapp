## Why

Les quatre premiers points fonctionnels du MVP (fiche client, vente à crédit, paiement, statut automatique) sont déjà couverts par des specs archivées (`add-client-and-credit-sale`, `record-payments`). Les deux derniers points du MVP (PRD §4, lignes 98-99) — mode mono-utilisateur et accès web basique mobile/ordinateur — sont déjà implémentés dans le code (`core/seller.py`, `templates/base.html`) mais n'ont jamais été formalisés en spec ni vérifiés explicitement. Sans spec, rien ne garantit que ce comportement reste intentionnel lors de la transition vers le multi-vendeur en V1, et la compatibilité mobile n'a jamais été validée avec Playwright comme l'exige CLAUDE.md.

## What Changes

- Formaliser le mode mono-utilisateur du MVP : toute vente/paiement est attribué à un unique compte vendeur bootstrap (`boutique`), créé automatiquement, sans écran de connexion ni gestion de comptes multiples.
- Formaliser l'exigence d'accès web basique : les pages de l'application doivent rester utilisables et lisibles à la fois sur mobile et sur ordinateur, via un simple navigateur, sans application dédiée.
- Vérifier avec Playwright (`playwright-skill`) que les pages existantes (accueil, liste clients, création client, création vente, détail client) restent fonctionnelles et lisibles sur un viewport mobile (ex. 390×844) et desktop (ex. 1280×800) ; corriger les régressions trouvées.
- Ne modifie pas le modèle de données ni les specs déjà archivées.

## Capabilities

### New Capabilities
- `single-user-access`: mode mono-utilisateur du MVP — attribution automatique des ventes/paiements à un compte vendeur bootstrap unique, sans authentification.
- `responsive-web-access`: accès web basique de l'application depuis un navigateur, sur mobile et sur ordinateur.

### Modified Capabilities
(aucune — les specs existantes ne changent pas de comportement)

## Impact

- Code concerné : `core/seller.py`, `core/views.py` (utilisation de `get_bootstrap_seller`), `templates/base.html` et gabarits associés (mise en page responsive).
- Pas de migration de base de données attendue.
- Vérification manuelle/Playwright des gabarits existants ; correctifs éventuels de mise en page mobile si des régressions sont trouvées.
