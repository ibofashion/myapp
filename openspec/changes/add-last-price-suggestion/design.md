## Context

Le formulaire de création de vente (`credit-sale-creation`) saisit chaque ligne avec un nom d'article libre, un prix unitaire et une quantité, sans catalogue ni table de prix (ARCHITECTURE.md, PRD §2.2). CLAUDE.md indique explicitement la requête à utiliser pour ce palier V2 : `DISTINCT ON (label) ... ORDER BY label, sold_at DESC` sur `SaleLine`, sans table dédiée. Voir proposal.md - Why pour la motivation.

## Goals / Non-Goals

**Goals:**
- Afficher le dernier prix pratiqué pour un article dès que son nom est reconnu, en réutilisant les données déjà présentes dans `SaleLine`.
- Garder la suggestion strictement indicative : aucune validation, aucun blocage, aucune modification du comportement de saisie existant.

**Non-Goals:**
- Autocomplétion ou liste de suggestions de noms d'articles (seul le prix d'un nom déjà saisi est concerné, pas la découverte de noms similaires).
- Historique des prix par article au-delà du dernier prix (pas de graphique d'évolution, pas de moyenne).

## Decisions

- **Requête** : `SaleLine.objects.filter(label=nom_saisi).order_by("-sale__sold_at").values("unit_price").first()`, équivalent fonctionnel au `DISTINCT ON (label) ... ORDER BY label, sold_at DESC` mentionné en CLAUDE.md mais filtré sur un seul nom exact à la fois (correspondance exacte demandée par la spec) plutôt qu'un `DISTINCT ON` global sur tous les articles — plus simple et suffisant puisque la suggestion n'est déclenchée que pour le nom en cours de saisie, pas pré-calculée pour tous les articles.
- **Déclenchement** : un endpoint HTMX (`GET /ventes/suggestion-prix/?article=<nom>`) appelé via `hx-get` sur le champ nom d'article de chaque ligne, avec `hx-trigger="change, keyup changed delay:500ms"` pour éviter une requête à chaque frappe, cohérent avec la contrainte réseau instable (ARCHITECTURE §6). La réponse est un fragment HTML minimal (texte de suggestion + bouton "Utiliser ce prix"), pas du JSON, pour rester dans le pattern HTMX déjà utilisé partout ailleurs dans l'app.
- **Application de la suggestion** : le bouton "Utiliser ce prix" remplit le champ prix de la ligne correspondante via un attribut Alpine.js local (pas de round-trip serveur supplémentaire), cohérent avec le choix déjà fait pour le formset de lignes de vente (Alpine gère l'état purement côté client, HTMX gère les données serveur).
- **Correspondance exacte du nom** : la comparaison est sensible à la casse et aux espaces exacts (pas de normalisation ni de recherche floue), pour rester simple et prévisible ; un nom légèrement différent ("Sac de riz" vs "sac de riz") ne déclenche pas de suggestion. Documenté comme limite connue plutôt que traité comme un défaut à corriger.

## Risks / Trade-offs

- [Une requête HTMX par ligne de vente à chaque changement de nom d'article peut multiplier les appels sur un formulaire à plusieurs lignes] → Acceptable pour le volume d'une boutique unique ; le `delay:500ms` limite déjà les appels redondants pendant la frappe.
- [La correspondance exacte sur le nom peut manquer des suggestions pertinentes pour des variantes proches du même article] → Accepté comme limite connue de ce palier V2 ; pas de recherche floue ni de normalisation ajoutée ici pour ne pas introduire de complexité non demandée par le PRD.
- [Absence de contrainte réseau garantissant que la suggestion arrive avant la validation du formulaire] → Sans conséquence : la suggestion est un simple pré-remplissage optionnel du champ prix existant, la validation de la vente ne dépend jamais de la réponse de cet endpoint.
