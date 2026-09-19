## 1. Autorisation

- [x] 1.1 Créer `core/authz.py` avec `can_edit_sale(user, sale)` (`role == "admin"` ou `sale.seller_id == user.id`) et un test unitaire couvrant les 3 cas (vendeur propriétaire, admin, vendeur tiers) dans `core/tests/test_authz.py`

## 2. Modification d'une vente

- [x] 2.1 Vérifier que `SaleLineFormSet` (`core/forms.py`, `inlineformset_factory`) gère `can_delete=True` pour retirer une ligne existante en édition ; ajuster si besoin
- [x] 2.2 Ajouter la vue `sale_edit` dans `core/views.py` : charge la vente, appelle `can_edit_sale` (403 si refusé via `PermissionDenied`), affiche/traite `SaleLineFormSet` lié à la vente existante (client et vendeur en lecture seule)
- [x] 2.3 Ajouter la route `sale_edit` dans `config/urls.py`
- [x] 2.4 Créer le template `core/sale_edit.html` (et fragment HTMX si soumission partielle, cohérent avec `core/sale_form.html`)
- [x] 2.5 Test : le vendeur d'origine modifie une ligne de sa vente et voit le total/solde mis à jour (`core/tests/test_sale_edit.py`)
- [x] 2.6 Test : un admin modifie la vente d'un autre vendeur avec succès
- [x] 2.7 Test : une modification qui viderait toutes les lignes est rejetée avec message d'erreur
- [x] 2.8 Test : un vendeur tiers accédant à l'URL de modification reçoit un 403 et aucune donnée n'est modifiée

## 3. Annulation (suppression) d'une vente

- [x] 3.1 Ajouter la vue `sale_delete` dans `core/views.py` : `transaction.atomic()`, appelle `can_edit_sale` (403 si refusé), vérifie l'absence de `PaymentAllocation` juste avant suppression, sinon renvoie une erreur explicite sans supprimer
- [x] 3.2 Ajouter la route `sale_delete` dans `config/urls.py`
- [x] 3.3 Ajouter une confirmation d'annulation (template ou fragment HTMX) avant suppression effective
- [x] 3.4 Test : le vendeur d'origine (ou un admin) annule une vente sans allocation → vente et lignes supprimées (`core/tests/test_sale_delete.py`)
- [x] 3.5 Test : annulation refusée si la vente a au moins une `PaymentAllocation`, avec message renvoyant à retirer l'imputation d'abord
- [x] 3.6 Test : un vendeur tiers accédant à l'URL d'annulation reçoit un 403 et la vente n'est pas supprimée

## 4. Interface

- [x] 4.1 Ajouter les actions « Modifier » et « Annuler » sur `core/sale_detail.html`, affichées uniquement quand `can_edit_sale(request.user, sale)` est vrai
- [x] 4.2 Test : les actions ne sont pas rendues dans le HTML pour un vendeur non autorisé consultant la fiche vente (`core/tests/test_sale_detail.py` ou équivalent)
- [x] 4.3 Vérifier avec `playwright-skill` le parcours modifier/annuler sur mobile et desktop (bouton désactivé pendant la requête, indicateur de chargement, cf. CLAUDE.md offline handling)

## 5. Validation finale

- [x] 5.1 Lancer `python -m pytest` et vérifier que la suite complète passe
- [x] 5.2 Lancer `ruff check .` et corriger les éventuels signalements sur les fichiers modifiés
