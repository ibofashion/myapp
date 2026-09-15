## Context

`core/seller.py` (`get_bootstrap_seller`) et `templates/base.html` implémentent déjà le mode mono-utilisateur et une mise en page responsive de base (Tailwind CDN, meta viewport, conteneur `max-w-4xl`). Voir proposal.md - Why. Ce changement formalise ce comportement en specs et vérifie qu'il tient sur l'ensemble des pages MVP existantes (accueil, liste clients, création client, création vente, détail client).

## Goals / Non-Goals

**Goals:**
- Documenter en specs le comportement mono-utilisateur déjà en place.
- Vérifier avec Playwright que chaque page fonctionnelle du MVP reste utilisable sur un viewport mobile (~390px) et desktop (~1280px).
- Corriger les régressions de mise en page mobile trouvées lors de la vérification (ex. débordement horizontal, navigation illisible).

**Non-Goals:**
- Ajouter une authentification ou une gestion de comptes multiples (réservé à la V1, cf. PRD §4).
- Remplacer Tailwind CDN par `django-tailwind` (hors périmètre sauf limitation bloquante, cf. CLAUDE.md).
- Modifier le modèle de données ou les règles métier des ventes/paiements.

## Decisions

- **Vérification via `playwright-skill` plutôt que tests Playwright dédiés au dépôt** : le MVP n'a pas encore de suite Playwright ; une vérification manuelle outillée suffit à ce stade et évite d'ajouter une dépendance de test avant que le besoin soit établi. Alternative écartée : écrire des tests Playwright persistants — reportée à une phase où l'UI se stabilise.
- **Aucun nouveau champ ni migration** : le compte bootstrap et la mise en page existent déjà ; ce changement documente et corrige, il ne redéfinit pas le modèle.

## Risks / Trade-offs

- [Le header de `base.html` (nav horizontale à 3 liens) pourrait déborder sur un très petit écran] → Vérifier explicitement à 390px de large lors du test Playwright ; ajuster en `flex-wrap` ou menu compact si besoin.
- [Les tableaux de ventes/paiements dans `client_detail.html` peuvent déborder horizontalement sur mobile] → Vérifier avec Playwright ; envelopper dans un conteneur `overflow-x-auto` si un débordement est constaté.
