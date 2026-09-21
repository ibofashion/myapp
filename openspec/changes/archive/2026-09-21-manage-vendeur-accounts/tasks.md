## 1. Autorisation

- [x] 1.1 Ajouter `is_admin(user)` dans `core/authz.py` et un test unitaire couvrant `role == "admin"` vrai/faux
- [x] 1.2 Ajouter un décorateur/mixin de vue qui appelle `is_admin` et renvoie 403 sinon, avec un test qui vérifie le 403 pour un utilisateur `vendeur`

## 2. Liste des comptes vendeurs

- [x] 2.1 Créer la vue et le template listant tous les comptes (identifiant, rôle), réservée aux admins
- [x] 2.2 Test : un admin authentifié voit tous les comptes existants avec leur rôle
- [x] 2.3 Test : un vendeur simple accédant directement à l'URL reçoit 403 et aucune donnée de compte

## 3. Création d'un compte vendeur

- [x] 3.1 Créer un `ModelForm` sur `User` (identifiant, mot de passe, rôle) avec validation de mot de passe Django
- [x] 3.2 Créer la vue de création (admin uniquement) et le template de formulaire
- [x] 3.3 Test : création réussie avec identifiant unique crée le compte et permet une connexion immédiate avec le rôle choisi
- [x] 3.4 Test : identifiant déjà utilisé est rejeté avec message d'erreur, sans création de doublon
- [x] 3.5 Test : un vendeur simple soumettant directement la requête de création reçoit 403 et aucun compte n'est créé

## 4. Modification du rôle d'un compte

- [x] 4.1 Créer la vue (admin uniquement) qui change le rôle d'un compte existant entre `admin` et `vendeur`
- [x] 4.2 Ajouter l'action de changement de rôle sur la page de liste des comptes
- [x] 4.3 Test : promotion `vendeur` → `admin` donne immédiatement les droits admin (ex. accès à la gestion des comptes)
- [x] 4.4 Test : rétrogradation `admin` → `vendeur` retire immédiatement les droits admin
- [x] 4.5 Test : un vendeur simple accédant directement à l'URL de changement de rôle reçoit 403 et le rôle cible reste inchangé

## 5. Navigation

- [x] 5.1 Ajouter un lien « Comptes vendeurs » dans la navigation, visible uniquement pour les admins, et vérifier qu'il est absent pour un vendeur simple
