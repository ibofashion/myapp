## 1. Requête du dernier prix pratiqué

- [x] 1.1 Écrire une fonction de service (ex. `core/price_suggestion.py`) qui retourne, pour un nom d'article exact donné, le prix unitaire de la ligne de vente la plus récente portant ce nom (`SaleLine.objects.filter(label=...).order_by("-sale__sold_at").values("unit_price").first()`), avec un test vérifiant que le prix de la vente la plus récente est retourné quand plusieurs prix existent pour le même nom
- [x] 1.2 Test : un nom d'article sans aucune vente antérieure retourne l'absence de suggestion (pas d'erreur)
- [x] 1.3 Test : la comparaison de nom est sensible à la casse et aux espaces exacts (une variante du nom ne retourne pas de suggestion)

## 2. Endpoint HTMX de suggestion

- [x] 2.1 Créer l'endpoint `GET /ventes/suggestion-prix/?article=<nom>` (login requis) qui appelle la fonction de service et rend un fragment HTML minimal (prix suggéré + bouton "Utiliser ce prix", ou fragment vide si aucune suggestion)
- [x] 2.2 Test : un utilisateur non authentifié appelant l'endpoint est refusé, sans donnée renvoyée

## 3. Intégration au formulaire de vente

- [x] 3.1 Ajouter `hx-get`/`hx-trigger="change, keyup changed delay:500ms"` sur le champ nom d'article de chaque ligne du formulaire de création de vente, ciblant un conteneur de suggestion propre à la ligne
- [x] 3.2 Ajouter le comportement Alpine.js du bouton "Utiliser ce prix" qui pré-remplit le champ prix de la ligne correspondante sans requête serveur supplémentaire
- [x] 3.3 Test manuel (Playwright) : saisir un nom d'article déjà vendu affiche la suggestion, saisir un nom jamais vendu n'affiche rien, et le prix saisi peut librement différer de la suggestion sans blocage ni message d'erreur
