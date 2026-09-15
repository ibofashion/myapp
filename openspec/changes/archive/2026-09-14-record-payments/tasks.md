## 1. Vue SQL et modèle de solde

- [x] 1.1 Écrire la migration `RunSQL` créant la vue `v_sale_balances` (avec SQL de rollback `DROP VIEW`) telle que définie dans ARCHITECTURE.md §3, et vérifier que `python manage.py migrate` l'applique sans erreur
- [x] 1.2 Ajouter le modèle non managé `SaleBalance` (`managed = False`, `db_table = "v_sale_balances"`) et vérifier qu'une requête `SaleBalance.objects.get(sale_id=...)` retourne `total`, `paid`, `balance`, `status` corrects pour une vente sans paiement (total = solde, statut `non_paye`)

## 2. Modèles Payment et PaymentAllocation

- [x] 2.1 Créer les modèles `Payment` et `PaymentAllocation` (ARCHITECTURE.md §2), avec la contrainte `CheckConstraint` `amount > 0` sur `PaymentAllocation`, et générer/appliquer la migration correspondante
- [x] 2.2 Ajouter les index sur `payment_allocations.sale_id` et `payment_allocations.payment_id`, et vérifier leur présence via `python manage.py sqlmigrate`
- [x] 2.3 Ajouter le champ de clé d'idempotence sur `Payment` en suivant le même mécanisme que celui utilisé pour `credit-sale-creation`, et vérifier qu'une contrainte d'unicité empêche deux paiements avec la même clé

## 3. Fonction métier record_payment

- [x] 3.1 Implémenter `record_payment(client, amount, allocations, recorded_by)` dans `transaction.atomic()` avec `select_for_update()` sur les ventes ciblées, triées par `id` pour un ordre de verrouillage stable, et vérifier par un test qu'un paiement valide crée le `Payment` et ses `PaymentAllocation`
- [x] 3.2 Ajouter la validation "somme des imputations == montant du paiement" et vérifier par un test qu'une répartition incomplète ou excédentaire est rejetée sans écriture en base
- [x] 3.3 Ajouter la validation "aucune vente ne dépasse son solde restant" en lisant le solde sous verrou, et vérifier par un test qu'une tentative de sur-paiement sur une vente est rejetée
- [x] 3.4 Ajouter la validation "chaque imputation est strictement positive" et vérifier par un test qu'une imputation à zéro est rejetée
- [x] 3.5 Ajouter la validation "toutes les ventes ciblées appartiennent au client du paiement" et vérifier par un test qu'une imputation sur la vente d'un autre client est rejetée
- [x] 3.6 Écrire le test de fumée en 4 étapes décrit dans ARCHITECTURE.md §8 (points 1 à 4 : création vente 10 000 → imputation 4 000 → imputation 6 000 → tentative de 1 de plus rejetée) et vérifier qu'il passe avec `pytest`

## 4. Vue liste des ventes d'un client avec solde

- [x] 4.1 Créer la vue Django affichant, pour un client donné, la liste de ses ventes avec total, payé, solde restant et statut (lecture de `SaleBalance`), et vérifier manuellement que les valeurs affichées correspondent au test de fumée de la tâche 3.6
- [x] 4.2 Gérer le cas d'un client sans aucune vente (message d'absence de vente) et vérifier ce cas par un test de vue
- [x] 4.3 Traduire visuellement le statut (`non_paye` / `partiel` / `solde`) dans le template et vérifier l'affichage sur les trois cas via `playwright-skill`

## 5. Formulaire de saisie de paiement

- [x] 5.1 Créer le formulaire HTMX de saisie d'un paiement pour un client : montant, puis sélection des ventes de ce client (avec leur solde restant courant affiché) et champ de montant imputé par vente sélectionnée
- [x] 5.2 Générer une clé d'idempotence envoyée avec la requête de soumission (même mécanisme que `credit-sale-creation` : rendue côté serveur dans un champ caché, régénérée à chaque affichage du formulaire), et vérifier qu'une double soumission avec la même clé ne crée qu'un seul paiement
- [x] 5.3 Brancher le formulaire sur `record_payment()` et afficher les messages d'erreur de validation (répartition incomplète/excédentaire, sur-paiement d'une vente, imputation nulle) renvoyés par la fonction métier
- [x] 5.4 Désactiver le bouton de soumission pendant l'envoi (`hx-disabled-elt`) avec indicateur de chargement (`hx-indicator`), conformément à ARCHITECTURE.md §6
- [x] 5.5 Vérifier le parcours complet (saisie paiement → imputation multi-ventes → mise à jour immédiate des soldes affichés) via `playwright-skill`, sur mobile et desktop

## 6. Validation finale

- [x] 6.1 Exécuter `python -m pytest` et vérifier que tous les tests (modèles, `record_payment`, vues) passent
- [x] 6.2 Exécuter `ruff check .` et corriger les éventuels signalements
- [x] 6.3 Exécuter `openspec validate record-payments --strict` et corriger les éventuels signalements
