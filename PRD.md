# Cahier des charges — Mini CRM de gestion des ventes à crédit

## 1. Contexte et problème initial

Le gestionnaire de boutique utilise actuellement l'application Notes de son téléphone pour lister, par client, les articles pris à crédit avec leur prix et leur date. Cette méthode pose deux problèmes majeurs :

- **Stockage anarchique** : les informations sont dispersées dans des dossiers sans structure.
- **Absence de calculs automatiques** : impossible d'obtenir automatiquement le prix unitaire, le prix total ou la quantité pour une vente.

L'objectif est de construire une application web de type mini CRM pour gérer les ventes à crédit, avec calculs automatiques et accès multi-utilisateur.

---

## 2. Modèle métier

### 2.1 Nature du "prêt"

Il s'agit de **vente à crédit** : le client reçoit définitivement l'article, mais doit encore payer tout ou partie de son prix. Ce n'est **pas** un prêt d'objet à restituer.

### 2.2 Règles métier validées

- Un client peut avoir **plusieurs ventes à crédit simultanées**.
- Il n'y a **pas de date d'échéance** de remboursement.
- Les prix des articles sont **négociables** (pas de catalogue à prix fixe).
- **Pas de suivi de stock** — uniquement la relation client ↔ article ↔ prix.
- Le remboursement peut être **partiel**.
- Le paiement se fait au niveau du **client** (pas directement lié à une vente à la saisie) : le client a une dette totale cumulée (somme de ses ventes non soldées).
- **Imputation manuelle** des paiements : lorsqu'un paiement arrive, le vendeur ou l'admin choisit lui-même sur quelle(s) vente(s) précise(s) du client l'appliquer.
- Chaque vente garde donc son propre solde restant et son propre statut.
- **Pas de traçabilité** des modifications (pas d'historique des changements).
- **Pas de fusion automatique** de clients homonymes.

### 2.3 Identification des clients

- Clé unique : **numéro de téléphone**.
- Le nom est une simple information descriptive (peut se répéter).
- Si un même client donne un numéro différent une fois → on crée une **nouvelle fiche** (pas de fusion).
- Si deux clients différents portent le même nom avec des numéros différents → on crée **deux fiches distinctes**.

### 2.4 Gestion des utilisateurs (vendeurs / admin)

- Chaque vendeur a un **compte individuel** (identifiant + mot de passe).
- Un vendeur voit **toutes les ventes de la boutique** (pas seulement les siennes).
- Un vendeur peut **modifier ou annuler ses propres ventes** uniquement.
- Un **rôle admin** existe : il peut modifier/annuler **toutes** les ventes (y compris celles des autres vendeurs) et gérer les comptes vendeurs.
- Accès nécessaire depuis **plusieurs appareils** → stockage centralisé en ligne (pas de fichier local).

### 2.5 Reprise des données existantes

Aucune reprise des anciennes données de l'app Notes n'est nécessaire — on part d'une base vide.

---

## 3. Modèle de données (entités principales)

### Client
- Numéro de téléphone (clé unique)
- Nom
- Liste de ses ventes à crédit
- Solde total dû (calculé = somme des soldes non soldés de ses ventes)

### Vente à crédit
- Client associé
- Vendeur associé (qui a enregistré la vente)
- Date de la vente
- Lignes d'articles :
  - Nom de l'article (texte libre)
  - Prix négocié (unitaire)
  - Quantité
  - Total ligne = prix unitaire × quantité (calcul automatique)
- Total de la vente = somme des totaux de lignes (calcul automatique)
- Solde restant sur cette vente (diminue à chaque paiement imputé dessus)
- Statut dérivé automatiquement : **non payé** / **partiel** / **soldé**

### Paiement
- Montant
- Date
- Client associé
- Répartition manuelle sur une ou plusieurs ventes précises de ce client (choisie par le vendeur/admin au moment de la saisie)

### Utilisateur (vendeur / admin)
- Identifiant / mot de passe
- Rôle : vendeur ou admin

---

## 4. Fonctionnalités par palier

### 🎯 MVP — Le strict nécessaire pour remplacer l'app Notes

But : résoudre le problème de calcul automatique et permettre de travailler au quotidien, même à un seul utilisateur.

- Créer une fiche client (nom + téléphone comme clé unique)
- Créer une vente à crédit : client + lignes d'articles (nom libre, prix négocié, quantité) avec calcul automatique du total par ligne et du total de la vente
- Voir la liste des ventes d'un client avec leur solde restant
- Enregistrer un paiement et l'imputer manuellement sur une ou plusieurs ventes du client
- Statut automatique par vente : non payé / partiel / soldé
- Un seul compte utilisateur (pas encore de multi-vendeur)
- Accès web basique (mobile + ordinateur) via navigateur

### 🚀 V1 — Version boutique complète

But : rendre l'application déployable pour toute l'équipe.

- Comptes vendeurs individuels (identifiant / mot de passe)
- Rôles : admin vs vendeur simple
- Chaque vendeur voit toutes les ventes de la boutique
- Un vendeur peut modifier/annuler **ses propres** ventes
- L'admin peut modifier/annuler **toutes** les ventes + gérer 
les comptes vendeurs
- Tableau de bord basique : total des dettes en cours (global + par client), total encaissé sur une période

### 📈 V2 — Confort et pilotage

But : affiner la gestion et gagner du temps sur les tâches répétitives.

- Tableau de bord enrichi : dettes par vendeur, liste triable des ventes non soldées
- Suggestion du dernier prix pratiqué pour un article donné (aide à la saisie, sans imposer de prix fixe)
- Export des données (PDF / Excel) pour archives ou comptabilité
- Recherche et filtrage avancés (par client, par période, par statut)
- Reçu imprimable/partageable après une vente ou un paiement

### 🚫 Hors périmètre (explicitement écarté)

- Gestion de stock / quantités disponibles
- Dates d'échéance et rappels de retard automatiques
- Traçabilité des modifications (historique des changements sur les ventes)
- Fusion automatique de fiches clients homonymes
- Catalogue d'articles à prix fixe

---

## 5. Notes pour l'agent de codage

- Application **web**, accessible depuis plusieurs appareils (mobile + desktop) → prévoir une base de données centralisée (pas de stockage local uniquement).
- Prévoir une authentification simple par identifiant/mot de passe dès la V1 (le MVP peut fonctionner sans authentification multi-utilisateur).
- Les calculs (total ligne, total vente, solde restant, statut) doivent être **dérivés automatiquement** — ne pas les stocker en dur sans recalcul, pour éviter les incohérences après un paiement partiel ou une modification.
- Le prix des articles n'est jamais figé dans un catalogue : chaque ligne de vente stocke son propre prix négocié.
