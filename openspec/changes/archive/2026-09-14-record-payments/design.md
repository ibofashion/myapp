## Context

`client-management` et `credit-sale-creation` existent déjà : modèles `Client`, `Sale`, `SaleLine`. Ce changement ajoute les paiements et la vue de solde par-dessus, sans toucher aux modèles existants. Voir proposal.md pour la motivation, et ARCHITECTURE.md §2-4 pour le modèle de données et les invariants déjà actés avec le porteur du projet.

## Goals / Non-Goals

**Goals:**
- Exposer le solde restant et le statut de chaque vente sans jamais les stocker en dur (source unique : la vue SQL `v_sale_balances`).
- Garantir les quatre invariants de l'imputation d'un paiement (ARCHITECTURE.md §4.1) même sous accès concurrent.
- Rendre la saisie de paiement idempotente sur réseau instable, comme la création de vente.

**Non-Goals:**
- Suppression ou ré-imputation d'une allocation existante (ARCHITECTURE.md §4.2) — traité dans un changement ultérieur.
- Authentification ou vérification de rôle sur qui peut enregistrer un paiement (MVP mono-utilisateur, PRD §4).
- Tableau de bord agrégé multi-clients (dette globale) — V1 (PRD §4).

## Decisions

### La vue `v_sale_balances` est créée par `migrations.RunSQL`, pas par un champ calculé Django
Alternative écartée : ajouter des champs `paid`/`balance`/`status` sur `Sale`, mis à jour par du code applicatif à chaque paiement. Rejeté car c'est exactement la source de dérive que CLAUDE.md et ARCHITECTURE.md §3 interdisent explicitement — un paiement supprimé ou une ligne de vente modifiée désynchroniserait ces champs. La vue SQL recalcule à chaque lecture, donc ne peut pas diverger.

### `record_payment()` est une fonction métier unique dans `transaction.atomic()` avec `select_for_update()`
Toutes les vérifications (répartition intégrale, non-dépassement par vente, montants positifs, appartenance au client) doivent être faites contre l'état verrouillé des ventes ciblées, pas contre une lecture antérieure — sinon deux paiements concurrents sur le même client pourraient tous deux passer la validation avant que l'un des deux ne soit committé, provoquant un sur-paiement. `select_for_update()` sur les `Sale` ciblées bloque cette course. Alternative écartée : valider en lisant `SaleBalance` sans verrou puis écrire — plus simple mais rouvre la fenêtre de course que l'app doit justement fermer (c'est l'opération la plus sensible de l'app, ARCHITECTURE.md §4.1).

### La clé d'idempotence du paiement suit le même mécanisme que celle de la vente
Pas de nouveau mécanisme à concevoir : même colonne/logique que `credit-sale-creation` (clé générée côté client, portée par la requête de création). Cohérence avec ARCHITECTURE.md §6 plutôt qu'une resolution ad hoc pour les paiements.

### Le formulaire de paiement affiche les ventes du client avec leur solde restant courant (lecture de `v_sale_balances`), pas une liste statique
Nécessaire pour que l'utilisateur voie combien il peut au maximum imputer sur chaque vente au moment de la saisie, et pour que la validation client-side (avant soumission) corresponde à la validation serveur.

## Risks / Trade-offs

- [Vue SQL non gérée par l'ORM] → Toute modification du schéma de `v_sale_balances` doit passer par une nouvelle migration `RunSQL`/`RunPython` avec le SQL de rollback correspondant ; documenté dans les tâches de migration.
- [`select_for_update()` sur plusieurs ventes en même temps] → Toujours verrouiller dans un ordre stable (ex. tri par `id`) pour éviter les interblocages si deux paiements concurrents touchent un ensemble de ventes qui se chevauche partiellement.
- [Formulaire d'imputation multi-ventes plus complexe côté UI qu'un simple montant] → Reste HTMX/Alpine.js (pas de nouvelle dépendance front), cases à cocher + champ montant par vente affichée, conforme à CLAUDE.md ("préférer les composants existants").
