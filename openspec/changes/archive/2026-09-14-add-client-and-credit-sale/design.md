## Context

Le dépôt ne contient aujourd'hui que des documents de planification (voir CLAUDE.md) : aucun projet Django n'est encore scaffoldé. Ce changement est donc le premier à toucher du code applicatif et doit poser le scaffolding minimal (projet Django, app, dépendances) nécessaire pour porter les deux capacités `client-management` et `credit-sale-creation`. Le modèle de données et les invariants de base sont déjà actés dans ARCHITECTURE.md §1-2 ; ce document ne les re-justifie pas, il précise seulement les décisions propres à ce premier changement.

## Goals / Non-Goals

**Goals:**
- Scaffolder le projet Django minimal permettant de faire tourner les modèles `Client`, `Sale`, `SaleLine` et leurs vues de création.
- Implémenter la création de client et la création de vente à crédit (avec lignes) telles que décrites dans les specs de ce changement.
- Poser une base d'app (`core`) et de conventions (settings, structure de dossiers) réutilisable par les changements suivants (paiements, soldes, statuts).

**Non-Goals:**
- Ne pas implémenter la vue `v_sale_balances`, le solde restant ni le statut dérivé (`non_payé`/`partiel`/`soldé`) — ce sera un changement dédié, une fois les paiements introduits.
- Ne pas implémenter l'authentification multi-utilisateur ni les rôles (V1, PRD §4) — un compte unique suffit pour le MVP.
- Ne pas implémenter la liste des ventes d'un client ni l'enregistrement de paiement (bullets suivants du MVP, hors périmètre de ce changement).

## Decisions

- **Structure du projet** : un seul projet Django (`config/` pour les settings, convention courante) avec une app `core` regroupant `Client`, `Sale`, `SaleLine` pour l'instant — pas de découpage en plusieurs apps tant qu'une seule capacité métier (ventes à crédit) existe. Alternative écartée : une app par modèle (`clients/`, `sales/`), jugée prématurée pour un MVP à deux capacités.
- **Utilisateur "vendeur" pour la FK `Sale.seller`** : ARCHITECTURE.md §2 définit `Sale.seller` comme `ForeignKey(User, on_delete=PROTECT)`, mais le MVP n'a pas encore d'authentification (PRD §5 : "le MVP peut fonctionner sans authentification multi-utilisateur"). Décision : créer un unique compte `User` (role `admin` par défaut) via une migration de données ou une commande `manage.py` d'amorçage, et l'assigner automatiquement comme `seller` de toute vente créée dans le MVP. Alternative écartée : rendre `seller` nullable — rejetée pour rester fidèle au modèle validé en ARCHITECTURE.md et éviter une migration de schéma dès la V1.
- **Formulaire de vente à lignes multiples** : un `Sale` avec ses `SaleLine` est saisi en un seul formulaire HTML utilisant un `inlineformset_factory` Django, avec ajout/suppression dynamique de lignes côté client géré par Alpine.js (pas de round-trip serveur pour ajouter une ligne vide). Alternative écartée : ajout de ligne via requête HTMX à chaque clic — plus simple ici de garder ça purement côté client (Alpine) puisqu'aucune donnée serveur n'est nécessaire pour afficher une ligne vide.
- **Calcul des totaux à l'affichage** : les totaux de ligne et de vente sont calculés en Python (propriété de modèle ou annotation de queryset), jamais stockés en colonne, conformément à la règle d'architecture sur les figures dérivées. La vue `v_sale_balances` (qui inclut aussi le solde et le statut) n'existe pas encore à ce stade puisqu'elle dépend des paiements ; jusqu'à son introduction, `Sale.total` est une propriété Python simple (`sum(line.total for line in self.lines.all())`), pas une requête SQL dédiée.
- **Normalisation du téléphone** : normalisation par une fonction pure `normalize_phone(raw: str) -> str` appelée dans `Client.save()` / dans le formulaire avant validation d'unicité, format E.164 si le numéro comporte un indicatif reconnaissable, sinon nettoyage des espaces/tirets. Le choix strict E.164 vs format local est noté comme detail d'implémentation ouvert dans ARCHITECTURE.md §9 — ce changement tranche pour une normalisation "best effort" (suppression espaces/tirets/points, ajout de l'indicatif par défaut si absent) plutôt qu'un rejet strict des formats non-E.164, pour ne pas bloquer la saisie rapide au comptoir.
- **Clé d'idempotence** : un champ `idempotency_key` (UUID, `unique`, généré côté client via Alpine/JS à l'affichage du formulaire) est ajouté sur `Sale`. La vue de création fait un `get_or_create` sur cette clé : si une vente avec la même clé existe déjà, elle est simplement retournée sans recréer de lignes. Alternative écartée : déduplication par un cache de requêtes récentes — moins fiable après un redémarrage du serveur ou sur plusieurs workers.

## Risks / Trade-offs

- [Le compte "vendeur" unique amorcé par migration devra être remplacé par de vrais comptes vendeurs en V1] → Mitigation : la FK `Sale.seller` reste inchangée entre MVP et V1, seule la façon de la peupler change (amorçage automatique vs. utilisateur connecté), donc pas de migration de schéma nécessaire à ce moment-là.
- [Normalisation "best effort" du téléphone peut laisser passer deux écritures différentes du même numéro si l'indicatif par défaut est mal deviné] → Mitigation : documenté comme limite connue (cohérent avec CLAUDE.md : "no dedup safety net if two writes format the same number differently"), pas de correctif automatique prévu ici.
- [Le formset Alpine.js pour les lignes de vente ajoute de la complexité côté template] → Mitigation : reste un pattern HTMX/Alpine standard, pas de nouvelle dépendance JS ajoutée (conforme à la contrainte "pas de SPA").

## Migration Plan

Aucune donnée existante à migrer (base vide, PRD §2.5). Étapes de déploiement : migrations Django standards (`makemigrations`/`migrate`) pour créer les tables `clients`, `sales`, `sale_lines`, `users`, puis exécution ponctuelle de la commande d'amorçage du compte vendeur unique.
