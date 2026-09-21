## 1. Agrégation des dettes en cours

- [x] 1.1 Écrire une fonction de service (ex. `core/dashboard.py`) qui agrège `SaleBalance` par client (`balance__gt=0`) et retourne la dette globale + le détail par client, avec un test vérifiant les totaux sur plusieurs clients et ventes
- [x] 1.2 Test : boutique sans aucune vente non soldée retourne une dette globale de 0 et un détail par client vide

## 2. Agrégation des encaissements par période

- [x] 2.1 Écrire une fonction qui calcule les bornes de date pour les présets « aujourd'hui / cette semaine / ce mois » à partir de `timezone.localtime(timezone.now())`, avec un test couvrant chaque préset
- [x] 2.2 Écrire une fonction qui somme `Payment.amount` sur `paid_at` dans les bornes calculées, avec un test vérifiant le total sur des paiements à cheval sur plusieurs périodes
- [x] 2.3 Test : aucune donnée de paiement sur la période sélectionnée retourne un total de 0

## 3. Vue et template du tableau de bord

- [x] 3.1 Créer la vue du tableau de bord (login requis, tout rôle) qui appelle les fonctions d'agrégation et lit le préset de période depuis le paramètre GET `periode` (défaut « aujourd'hui »)
- [x] 3.2 Créer le template affichant la dette globale, le détail par client, le sélecteur de préset et le total encaissé
- [x] 3.3 Test : un utilisateur non authentifié accédant à l'URL du tableau de bord est redirigé vers la connexion, sans montant affiché
- [x] 3.4 Test : un vendeur simple authentifié voit les mêmes totaux qu'un admin sur le tableau de bord

## 4. Navigation

- [x] 4.1 Ajouter un lien « Tableau de bord » dans la navigation pour tout utilisateur authentifié et vérifier son affichage pour les deux rôles
