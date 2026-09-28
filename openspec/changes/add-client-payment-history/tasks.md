## 1. Chargement des données

- [x] 1.1 Dans `client_detail` (`core/views.py`), charger les paiements du client (`client.payments`) triés par `-paid_at`, avec `prefetch_related("allocations__sale")` pour éviter les requêtes N+1, et les passer au contexte sous `payments`
- [x] 1.2 Vérifier via `python manage.py shell` ou un test que le nombre de requêtes SQL reste constant quel que soit le nombre de paiements/imputations (pas de N+1)

## 2. Affichage

- [x] 2.1 Ajouter dans `templates/core/_client_detail_fragment.html` une section "Historique des paiements" listant `payments` (date, montant), du plus récent au plus ancien
- [x] 2.2 Pour chaque paiement, afficher le détail de ses imputations (`payment.allocations.all`) : numéro de vente en lien vers `sale_detail`, et montant imputé
- [x] 2.3 Afficher un message explicite ("Aucun paiement enregistré pour ce client.") quand la liste est vide
- [x] 2.4 Vérifier visuellement que la section reste cohérente avec le style Tailwind existant de la page (mêmes cartes/tableaux que les sections voisines)

## 3. Tests

- [x] 3.1 Ajouter un test dans `core/tests/test_client_detail_view.py` : un client avec un paiement imputé sur une seule vente voit ce paiement et cette imputation affichés sur sa fiche
- [x] 3.2 Ajouter un test : un client avec un paiement réparti sur deux ventes voit les deux imputations affichées avec les bons montants
- [x] 3.3 Ajouter un test : un client sans paiement voit le message d'historique vide
- [x] 3.4 Lancer `python -m pytest core/tests/test_client_detail_view.py` et vérifier que tous les tests passent

## 4. Validation manuelle

- [x] 4.1 Lancer le serveur de dev, créer un client, une vente et un paiement partiel, puis vérifier dans le navigateur que l'historique apparaît immédiatement après soumission du formulaire de paiement (rendu HTMX du fragment)
- [x] 4.2 Exécuter un test Playwright (`playwright-skill`) couvrant : création client → vente → paiement → apparition de l'historique avec date/montant/imputation, sur mobile et desktop (responsive)
