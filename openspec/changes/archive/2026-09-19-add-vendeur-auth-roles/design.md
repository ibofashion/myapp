## Context

Le champ `role` existe déjà sur `core.User` (`core/models.py:9-11`, choix `vendeur`/`admin`). Le MVP attribue vendes et paiements via `core.seller.get_bootstrap_seller()`, appelé depuis `sale_create` et `client_detail` (`core/views.py`), qui crée/récupère un unique compte `boutique` à mot de passe inutilisable. Aucune vue n'exige actuellement de session authentifiée : `AUTH_USER_MODEL = 'core.User'`, `django.contrib.auth` et `AuthenticationMiddleware` sont déjà dans `INSTALLED_APPS`/`MIDDLEWARE`, mais aucune vue de connexion, aucun `LOGIN_URL`, aucune protection `login_required` n'existent encore. Voir proposal.md pour le pourquoi.

## Goals / Non-Goals

**Goals:**
- Exiger une session authentifiée pour toutes les pages fonctionnelles actuelles (`home`, `client_list`, `client_create`, `client_detail`, `sale_create`, `sale_detail`).
- Remplacer `get_bootstrap_seller()` par `request.user` comme vendeur/auteur dans `sale_create` et `client_detail` (paiement).
- Fournir un écran de connexion/déconnexion minimal, cohérent avec le style Tailwind existant.
- Permettre à l'admin de créer des comptes vendeurs via Django Admin (le champ `role` doit y être éditable).

**Non-Goals:**
- Pas d'interface applicative dédiée à la gestion des comptes (création/désactivation de vendeurs) en dehors de Django Admin.
- Pas d'application de `can_edit_sale` ni de restriction d'édition/suppression par vendeur — toutes les pages listées restent en lecture/écriture pour tout vendeur connecté, comme aujourd'hui.
- Pas de tableau de bord.
- Pas de migration ou réattribution des ventes/paiements déjà enregistrés sous le compte bootstrap.

## Decisions

**Protection des vues : `LoginRequiredMiddleware`-style via décorateur sur chaque vue plutôt que middleware global.**
Utiliser `@login_required` (ou `LoginRequiredMixin` si les vues passent en CBV) sur chacune des six vues fonctionnelles, plutôt qu'un middleware global qui protégerait tout, y compris `/admin/` (déjà protégé séparément par Django) et d'éventuelles futures routes publiques (ex. healthcheck). Alternative écartée : middleware `LoginRequiredMiddleware` (Django 5.1+) sur tout le site — rejeté pour garder un contrôle explicite vue par vue, cohérent avec le principe d'autorisation centralisée mais explicite déjà retenu pour `can_edit_sale` (ARCHITECTURE.md §5).

**`LOGIN_URL` pointe vers une vue de connexion maison, pas `django.contrib.auth.views.LoginView` brute.**
Utiliser `django.contrib.auth.views.LoginView`/`LogoutView` avec un template maison (`core/login.html`) plutôt que ré-implémenter la logique d'authentification — pas de raison de s'écarter du provider standard Django déjà choisi (ARCHITECTURE.md §1 : « Auth : `django.contrib.auth`, sessions, provider identifiant/mot de passe »).

**Suppression de `get_bootstrap_seller()` et du champ `idempotency_key` reste inchangé.**
`sale_create` et `client_detail` utilisent désormais `request.user` directement comme `seller`/`recorded_by`. `core/seller.py` est supprimé une fois ses deux appelants migrés. Alternative écartée : garder `get_bootstrap_seller()` comme filet de repli si `request.user` n'est pas authentifié — rejetée car `@login_required` garantit déjà qu'aucune vue protégée n'est atteinte sans utilisateur authentifié, un filet de repli masquerait un bug plutôt que de le révéler.

**Comptes vendeurs créés via Django Admin uniquement.**
`role` est déjà un champ du modèle `User` ; il suffit de l'exposer dans `UserAdmin` (`fieldsets`/`list_display`) pour que l'admin puisse créer un compte vendeur avec identifiant, mot de passe et rôle sans écran applicatif dédié — conforme à ARCHITECTURE.md §1 et au choix de périmètre du proposal.

**Aucun filtrage par vendeur sur les vues de consultation.**
`client_detail`, `sale_detail`, `client_list` restent des requêtes non filtrées par `seller` — c'est déjà leur comportement actuel (aucun `.filter(seller=request.user)` n'existe). Le seul changement est l'ajout de `@login_required` ; aucune requête ORM n'a besoin d'être modifiée pour la visibilité.

## Risks / Trade-offs

- **[Risque]** Le compte bootstrap `boutique` reste en base avec un mot de passe inutilisable après ce change, et continue d'apparaître comme vendeur sur les ventes/paiements historiques du MVP → **Mitigation** : accepté explicitement dans le proposal (Impact), aucune donnée de production à migrer à ce stade (PRD §2.5) ; l'admin peut le renommer ou lui attribuer un mot de passe utilisable via Django Admin s'il souhaite le réutiliser comme compte vendeur réel.
- **[Risque]** Oublier `@login_required` sur une des six vues laisserait une page accessible sans authentification → **Mitigation** : test Playwright de bout en bout vérifiant que chaque URL fonctionnelle redirige vers la connexion sans session (voir tasks.md).
- **[Risque]** Un mot de passe faible pour un compte vendeur créé via Django Admin → **Mitigation** : validateurs de mot de passe standard Django (`AUTH_PASSWORD_VALIDATORS`, déjà activés par défaut par `django-admin startproject`) s'appliquent à la création via l'admin.

## Migration Plan

1. Ajouter `LOGIN_URL`, `LOGIN_REDIRECT_URL`, `LOGOUT_REDIRECT_URL` dans `config/settings.py`.
2. Ajouter les routes `login`/`logout` dans `config/urls.py` et le template `core/login.html`.
3. Décorer les six vues fonctionnelles avec `@login_required`.
4. Remplacer les appels `get_bootstrap_seller()` par `request.user` dans `sale_create` et `client_detail`, puis supprimer `core/seller.py`.
5. Exposer `role` dans `UserAdmin` (`core/admin.py`).
6. Déployer : aucune migration de schéma nécessaire (le champ `role` existe déjà) ; le compte `boutique` existant n'est pas supprimé.
7. Rollback : revert du commit — aucune donnée n'est perdue puisque `role` et les comptes existants restent inchangés.
