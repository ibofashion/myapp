## 1. Agrégation de la dette par vendeur

- [ ] 1.1 Étendre `core/dashboard.py` avec une fonction qui agrège `SaleBalance` par vendeur (`balance__gt=0`, groupé sur `sale__vendeur`), avec un test vérifiant les totaux sur plusieurs vendeurs et ventes
- [ ] 1.2 Test : un vendeur sans vente non soldée n'apparaît pas dans le résultat de l'agrégation
- [ ] 1.3 Test : la somme des totaux par vendeur est égale à la dette globale déjà calculée (§ dashboard V1)

## 2. Liste triable des ventes non soldées

- [ ] 2.1 Écrire une fonction qui retourne les ventes avec `balance__gt=0` (statut non payé ou partiel), incluant date de vente, client, vendeur et solde restant, avec un paramètre de tri (`champ`, `sens`) restreint à un mapping explicite (date, solde, client, vendeur)
- [ ] 2.2 Test : tri par solde restant décroissant retourne les ventes dans le bon ordre
- [ ] 2.3 Test : tri par date de vente (croissant et décroissant) retourne les ventes dans le bon ordre
- [ ] 2.4 Test : boutique sans vente non soldée retourne une liste vide sans erreur

## 3. Vue et endpoint HTMX

- [ ] 3.1 Étendre la vue du tableau de bord pour inclure la répartition par vendeur dans le contexte du template
- [ ] 3.2 Créer l'endpoint HTMX `GET /dashboard/ventes-non-soldees/` (login requis) qui rend uniquement le fragment `<table>` de la liste triée selon les paramètres `tri`/`sens` de la requête
- [ ] 3.3 Test : un utilisateur non authentifié appelant l'endpoint HTMX est refusé (redirection ou 403), sans donnée renvoyée

## 4. Template du tableau de bord

- [ ] 4.1 Ajouter la section « dette par vendeur » au template du tableau de bord, à côté de la dette par client existante
- [ ] 4.2 Ajouter la section « ventes non soldées » avec en-têtes de colonnes cliquables (`hx-get` vers l'endpoint de tri, `hx-target` sur le corps du tableau)
- [ ] 4.3 Test : un vendeur simple authentifié voit les mêmes sections (dette par vendeur, ventes non soldées) qu'un admin, avec les mêmes données
