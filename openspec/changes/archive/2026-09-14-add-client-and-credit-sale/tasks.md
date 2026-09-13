## 1. Scaffolding du projet Django

- [x] 1.1 Créer `requirements.txt` (Django 5, psycopg, pytest-django) et un venv documenté ; vérifier `pip install -r requirements.txt` réussit
- [x] 1.2 Scaffolder le projet Django (`django-admin startproject config .`) et l'app `core` (`python manage.py startapp core`) ; vérifier `python manage.py runserver` démarre sans erreur
- [x] 1.3 Configurer `settings.py` pour PostgreSQL (variables d'environnement pour la connexion) et enregistrer l'app `core` ; vérifier `python manage.py check` passe
- [x] 1.4 Ajouter Tailwind CSS (CDN) et HTMX + Alpine.js au template de base ; vérifier qu'une page de test les charge sans erreur console

## 2. Modèle Client

- [x] 2.1 Implémenter la fonction pure `normalize_phone(raw: str) -> str` (module `core/phone.py`) ; vérifier par des tests unitaires que des formats équivalents (espaces, tirets, indicatif) produisent la même sortie
- [x] 2.2 Créer le modèle `Client` (`phone` unique, `name`) et sa migration ; vérifier `python manage.py migrate` crée la table avec la contrainte d'unicité
- [x] 2.3 Créer le formulaire `ClientForm` qui normalise le téléphone avant validation d'unicité ; vérifier un test qui soumet un doublon normalisé et confirme le rejet
- [x] 2.4 Créer la vue + template de création de client (HTMX, bouton désactivé pendant l'envoi via `hx-disabled-elt`) ; vérifier manuellement la création d'un client depuis le navigateur
- [x] 2.5 Écrire les tests `pytest-django` couvrant les scénarios de la spec `client-management` (création réussie, téléphone manquant, doublon rejeté, homonymes acceptés) ; vérifier que la suite passe

## 3. Modèle User d'amorçage (support de `Sale.seller`)

- [x] 3.1 Créer le modèle `User` (`AbstractUser` + champ `role`, défaut `admin`) minimal requis par ARCHITECTURE.md §2 ; vérifier la migration s'applique
- [x] 3.2 Ajouter une commande de gestion (`manage.py bootstrap_seller`) ou une migration de données créant l'unique compte vendeur du MVP ; vérifier qu'après `migrate` un `User` existe et est réutilisé si la commande est relancée (idempotent)

## 4. Modèle Vente à crédit

- [x] 4.1 Créer les modèles `Sale` (dont `idempotency_key` unique) et `SaleLine` (label, unit_price, quantity) avec leurs migrations ; vérifier `python manage.py migrate` réussit et les contraintes (FK, `PositiveIntegerField`) sont posées
- [x] 4.2 Ajouter les propriétés Python de calcul (`SaleLine.total`, `Sale.total`) sans colonne stockée ; vérifier un test unitaire sur les exemples de la spec (1500×3=4500, 4500+2000=6500)
- [x] 4.3 Créer le `SaleForm` + `inlineformset_factory` pour les lignes, avec validation (au moins une ligne, quantité > 0, prix ≥ 0) ; vérifier des tests couvrant vente sans client, vente sans ligne, ligne invalide
- [x] 4.4 Créer la vue de création de vente : génération de la clé d'idempotence côté client (Alpine.js) et `get_or_create` côté serveur sur `idempotency_key` ; vérifier un test simulant une double soumission avec la même clé ne crée qu'une seule vente
- [x] 4.5 Créer le template de saisie de vente (sélection client, ajout/suppression dynamique de lignes en Alpine.js, affichage live du total ligne et total vente, `hx-disabled-elt` + `hx-indicator` sur soumission) ; vérifier manuellement dans le navigateur
- [x] 4.6 Écrire les tests `pytest-django` couvrant les scénarios restants de la spec `credit-sale-creation` (prix négocié propre à chaque ligne) ; vérifier que la suite passe

## 5. Validation de bout en bout

- [x] 5.1 Test Playwright : créer un client puis une vente à deux lignes depuis l'interface, vérifier l'affichage correct des totaux ligne et vente
- [x] 5.2 Vérifier la responsivité mobile/desktop des deux formulaires (client et vente) avec `playwright-skill`, conformément à CLAUDE.md
- [x] 5.3 Exécuter `ruff check .` et la suite `pytest` complète ; vérifier qu'ils passent sans erreur
