## Context

Le tableau de bord V1 (`2026-09-21-add-basic-dashboard`) calcule déjà la dette globale et par client via une agrégation sur `SaleBalance` (`values("client_id", ...).annotate(total_due=Sum("balance"))`), et le total encaissé par préset de période via `Payment`. Voir proposal.md - Why pour la motivation de cet enrichissement. `Sale` porte déjà une FK vers le vendeur qui l'a enregistrée (`vendeur-accounts`), donc grouper par vendeur ne demande aucune nouvelle donnée.

## Goals / Non-Goals

**Goals:**
- Étendre le même principe d'agrégation en lecture (pas de champ stocké) à un regroupement par vendeur.
- Rendre la liste des ventes non soldées triable sans recharger toute la page (cohérent avec l'usage HTMX déjà en place ailleurs dans l'app).

**Non-Goals:**
- Pagination de la liste des ventes non soldées (hors périmètre pour ce palier ; le volume d'une boutique unique reste faible — à revisiter seulement si mesuré comme un problème réel).
- Filtrage par période ou par client sur la liste des ventes non soldées (déjà couvert par la recherche/filtrage avancés prévue plus tard au palier V2, hors du présent changement).

## Decisions

- **Dette par vendeur** : une requête `SaleBalance.objects.filter(balance__gt=0).values("sale__vendeur_id", "sale__vendeur__username").annotate(total_due=Sum("balance"))`, sur le même modèle que la dette par client déjà existante — même page, même coût, pas de nouvelle jointure lourde.
- **Liste triable** : un seul endpoint HTMX (`GET /dashboard/ventes-non-soldees/?tri=<champ>&sens=<asc|desc>`) qui renvoie uniquement le fragment `<table>` de la liste, déclenché par un clic sur l'en-tête de colonne (`hx-get` + `hx-target` sur le corps du tableau). Le tri est appliqué côté serveur via `order_by()` sur le queryset `SaleBalance.objects.filter(balance__gt=0)`, jamais côté client, pour rester cohérent avec le principe qu'aucun total ou classement n'est recalculé en JS.
- **Colonnes triables** : date de vente (`sale__sold_at`), solde restant (`balance`), client (`sale__client__name`), vendeur (`sale__vendeur__username`) — un mapping explicite entre paramètre `tri` et expression `order_by()` côté vue, pour éviter d'exposer un nom de champ ORM arbitraire dans l'URL.

## Risks / Trade-offs

- [Le tri par client ou par vendeur sur un nom peut être ambigu en cas d'homonymes] → Accepté : le tri reste un confort de lecture, pas une clé d'identification ; l'ambiguïté des noms est déjà une règle métier connue (PRD §2.3).
- [Ajout d'un endpoint HTMX supplémentaire à sécuriser] → Réutilise la même exigence d'authentification que le reste du tableau de bord (`dashboard` §"Tableau de bord accessible à tout utilisateur authentifié"), sans nouvelle règle d'autorisation à inventer.
