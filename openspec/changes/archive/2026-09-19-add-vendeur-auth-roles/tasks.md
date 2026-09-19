## 1. Configuration de l'authentification

- [x] 1.1 Ajouter `LOGIN_URL = 'login'`, `LOGIN_REDIRECT_URL = 'home'`, `LOGOUT_REDIRECT_URL = 'login'` dans `config/settings.py` et vérifier que le serveur démarre sans erreur de configuration
- [x] 1.2 Ajouter les routes `login/` et `logout/` dans `config/urls.py` via `django.contrib.auth.views.LoginView`/`LogoutView` et vérifier que `python manage.py show_urls` (ou l'inspection de `urlpatterns`) les liste
- [x] 1.3 Créer le template `core/templates/core/login.html` (formulaire identifiant/mot de passe, style Tailwind cohérent avec les gabarits existants) et vérifier son rendu en ouvrant `/login/` dans un navigateur

## 2. Protection des vues fonctionnelles

- [x] 2.1 Ajouter `@login_required` à `home`, `client_list`, `client_create`, `client_detail`, `sale_create`, `sale_detail` dans `core/views.py`
- [x] 2.2 Écrire un test `pytest-django` qui vérifie que chacune des six URLs fonctionnelles redirige vers `/login/` pour un client non authentifié
- [x] 2.3 Écrire un test `pytest-django` qui vérifie qu'un utilisateur authentifié accède normalement à chacune des six URLs

## 3. Attribution au vendeur authentifié

- [x] 3.1 Remplacer `sale.seller = get_bootstrap_seller()` par `sale.seller = request.user` dans `sale_create` (`core/views.py`)
- [x] 3.2 Remplacer `recorded_by=get_bootstrap_seller()` par `recorded_by=request.user` dans `client_detail` (`core/views.py`)
- [x] 3.3 Supprimer `core/seller.py` et vérifier qu'aucune référence à `get_bootstrap_seller` ne subsiste (`grep -r get_bootstrap_seller`)
- [x] 3.4 Écrire un test `pytest-django` : un vendeur authentifié crée une vente, puis vérifier que `sale.seller == vendeur_connecté`
- [x] 3.5 Écrire un test `pytest-django` : un vendeur authentifié enregistre un paiement, puis vérifier que `payment.recorded_by == vendeur_connecté`

## 4. Comptes vendeurs et rôles dans Django Admin

- [x] 4.1 Enregistrer/étendre `UserAdmin` dans `core/admin.py` pour exposer le champ `role` en création et édition, et vérifier dans `/admin/core/user/add/` qu'un compte vendeur peut être créé avec un rôle choisi
- [x] 4.2 Écrire un test `pytest-django` créant deux comptes (rôles `admin` et `vendeur`) via l'ORM et vérifiant que chacun peut se connecter (`client.login`) indépendamment de l'autre

## 5. Visibilité partagée des ventes

- [x] 5.1 Écrire un test `pytest-django` : deux vendeurs authentifiés distincts, l'un crée une vente pour un client, l'autre consulte `client_detail` et `sale_detail` de cette vente et obtient un statut 200 avec le contenu attendu (aucun filtrage par vendeur)

## 6. Vérification bout en bout

- [x] 6.1 Lancer `playwright-skill` : parcours connexion → création de vente → déconnexion → tentative d'accès direct à une page fonctionnelle sans session (doit rediriger vers la connexion), sur viewport mobile et desktop
- [x] 6.2 Exécuter la suite `pytest` complète et vérifier qu'elle passe sans régression sur les tests existants (client, vente, paiement)
