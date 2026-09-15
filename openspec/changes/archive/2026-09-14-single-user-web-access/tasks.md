## 1. Vérification du mode mono-utilisateur

- [x] 1.1 Relire `core/seller.py` et `core/views.py` pour confirmer que toute création de vente et de paiement passe par `get_bootstrap_seller()`, sans champ de sélection de vendeur exposé dans `SaleForm`/`PaymentForm` ni leurs gabarits
- [x] 1.2 Confirmer qu'aucune page fonctionnelle (`/`, `/clients/`, `/clients/nouveau/`, `/clients/<id>/`, `/ventes/nouvelle/`) ne redirige vers un écran de connexion, en listant `config/urls.py` et en vérifiant l'absence de middleware d'authentification actif sur ces vues
- [x] 1.3 Écrire/compléter un test (`core/tests/`) qui crée une vente et un paiement sur une base sans compte vendeur préexistant et vérifie qu'un unique compte bootstrap est créé puis réutilisé (`python -m pytest`)

## 2. Vérification de l'accès web responsive

- [x] 2.1 Lancer le serveur de dev (`python manage.py runserver`) et utiliser `playwright-skill` pour visiter l'accueil, la liste des clients, la création de client, la création de vente et le détail client sur un viewport mobile (~390×844)
- [x] 2.2 Répéter la vérification Playwright sur un viewport desktop (~1280×800) pour les mêmes pages
- [x] 2.3 Noter toute régression trouvée (débordement horizontal, navigation illisible, formulaire tronqué) et corriger les gabarits concernés (`templates/base.html`, `templates/core/*.html`) — aucune régression trouvée, aucun correctif nécessaire
- [x] 2.4 Revérifier avec Playwright après correction que les pages corrigées s'affichent correctement sur les deux viewports — sans objet (aucune correction requise)

## 3. Clôture

- [x] 3.1 Exécuter la suite de tests complète (`python -m pytest`) et confirmer qu'elle passe
- [x] 3.2 Mettre à jour `proposal.md`/`design.md` si des ajustements de mise en page non prévus ont été nécessaires — sans objet (aucun ajustement de mise en page non prévu)
