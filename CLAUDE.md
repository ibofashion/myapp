# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Documentation lookup

Utilise toujours context7 lorsque j'ai besoin de génération de code, d'étapes de configuration ou d'installation, ou de documentation de bibliothèque/API. Cela signifie que tu dois automatiquement utiliser les outils MCP Context7 pour résoudre l'identifiant de bibliothèque et obtenir la documentation de bibliothèque sans que j'aie à le demander explicitement.

## Project status

This repository currently contains only planning documents — no application code has been scaffolded yet (no `manage.py`, no `requirements.txt`, not yet a git repo). Read [`PRD.md`](./PRD.md) and [`ARCHITECTURE.md`](./ARCHITECTURE.md) in full before writing code; they are the authoritative spec and the architecture decisions were already validated with the project owner (see PRD §5 and ARCHITECTURE §9). Do not re-litigate decisions marked as settled in those files.

Once the Django project is scaffolded, standard commands will be:
- Run dev server: `python manage.py runserver`
- Run migrations: `python manage.py makemigrations` / `python manage.py migrate`
- Run tests: `python -m pytest` (single test: `python -m pytest path/to/test_file.py::test_name`)
- Lint: `ruff check .`

## What this app is

A mini CRM for a shop owner to replace tracking credit sales (*ventes à crédit*) in a phone Notes app. A client takes goods immediately but pays later, in full or in installments, with no due date. This is **not** a loan-of-object system — goods are never returned.

## Stack (see ARCHITECTURE.md §1 for full rationale)

- Python 3.12+, Django 5 (LTS), PostgreSQL, Django ORM
- HTMX + Alpine.js for interactivity — **no SPA/frontend framework**
- Tailwind CSS (CDN for MVP; revisit `django-tailwind` only if the CDN becomes limiting)
- `pytest-django` for business logic tests, Playwright for user-flow tests
- `pip` + `venv` (`requirements.txt`) — not poetry/uv
- Target host: Railway Hobby (app + Postgres together)
- Currency: **XOF (franc CFA)** — integer amounts only, no decimal subunit. Always use `DecimalField(max_digits=12, decimal_places=0)`, never `float`, for money.

## Core domain model

- **Client**: unique key is `phone` (normalized before insert — no dedup safety net if two writes format the same number differently). `name` is just descriptive text and may repeat. No automatic merging of same-name clients — see PRD §2.3.
- **Sale**: belongs to a client and a seller; has `SaleLine`s (free-text article label, negotiated `unit_price`, `quantity` — there is intentionally no article catalog and no stock tracking).
- **Payment**: recorded against a **client**, not a sale. The vendeur/admin manually allocates (`PaymentAllocation`) a payment across one or more of that client's sales at entry time — this allocation is never automatic/FIFO.
- No audit trail / change history is stored anywhere (explicit non-requirement, PRD §2.2 and §4 "hors périmètre") — don't add one speculatively.

## The one architectural rule that matters most

**All derived financial figures (line total, sale total, balance, status) must never be stored/hand-recalculated — they come from the `v_sale_balances` SQL view** (ARCHITECTURE.md §3), exposed via the unmanaged `SaleBalance` model. A client's total debt and any dashboard aggregate must be computed by querying/aggregating this view, never by maintaining a `total_due` field that's updated on each payment. This exists specifically to prevent drift after partial payments or sale edits.

## Sensitive invariants

**Recording a payment** (ARCHITECTURE §4.1) is the most sensitive operation in the app. It must run inside `transaction.atomic()` with `select_for_update()` on the affected sales, and must enforce:
- Sum of a payment's allocations == the payment amount (no partial allocation left dangling).
- Sum of allocations on a sale never exceeds that sale's total (no over-payment).
- Every allocation amount is `> 0`.
- All targeted sales belong to the payment's client.

**Deleting a sale** (ARCHITECTURE §4.2) is a hard delete (no archiving), but is blocked if the sale already has any `PaymentAllocation` — allocations must be removed/reassigned first, otherwise the source payment would no longer be fully allocated.

**Authorization** is centralized in a single `can_edit_sale(user, sale)` function (`core/authz.py`) — `role == "admin"` or the requesting user is the sale's seller. Every sale edit/delete view must call this server-side; never rely on hiding a button in a template, and don't duplicate this check inline elsewhere.

## Deliberately out of scope

Do not add unless explicitly requested: stock/inventory tracking, due dates or automatic overdue reminders, change-history/audit trail, automatic merging of same-name clients, a fixed-price article catalog. These are explicitly excluded in PRD §4.

## Feature tiers

Work is staged as MVP → V1 → V2 (PRD §4). MVP is single-user, no auth required yet. V1 adds individual vendeur accounts, roles, and a basic dashboard. V2 adds richer dashboards, last-price suggestions (via `DISTINCT ON (label) ... ORDER BY label, sold_at DESC` over `SaleLine`, no dedicated table), exports, search/filter, and printable receipts. Check which tier a request belongs to before over-building.

## Offline/flaky-network handling

Shop connectivity is unreliable (ARCHITECTURE §6): disable submit buttons during requests (`hx-disabled-elt`) with a loading indicator (`hx-indicator`), and use a client-generated idempotency key on sale/payment creation so a double-tap on a slow connection doesn't create duplicates.
