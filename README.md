# LOGOSFORGE

A local-first editorial management platform for publishing houses.
LOGOSFORGE is intended as a quiet, archival workspace for the daily
ledger of a press — manuscripts, authors, contracts, and production —
under a single, refined surface.

This repository contains the foundation and the editorial domain
schema. HTTP endpoints and UI for the domain will follow in successive
editions.

---

## Architecture

| Layer    | Choice                                          |
| -------- | ----------------------------------------------- |
| Backend  | Python 3.11+, FastAPI, SQLModel, Uvicorn        |
| Database | SQLite (local-first), PostgreSQL ready          |
| Frontend | React 18, Vite 5, TypeScript, TailwindCSS 3     |
| Theme    | Dark, editorial, archival                       |

```
backend/
  app/
    main.py        FastAPI application factory
    db.py          Engine, session, init_db
    config.py      Settings (env-driven)
    seed.py        Schema initialisation + sample data
    models/        SQLModel domain entities + enums
    routers/       HTTP routers (health, meta, …)
    services/      Business logic
    schemas/       Request/response payloads
    utils/         Cross-cutting helpers
  tests/           Pytest suite (model + relationship checks)

frontend/
  src/
    main.tsx       React entrypoint
    App.tsx        Root component
    pages/         Page components (Dashboard)
    components/    Reusable UI primitives
    layouts/       Application shell
    api/           Typed API client
    types/         Shared TypeScript types
```

---

## Prerequisites

- Python **3.11+**
- Node.js **20+** (22 recommended) with npm
- A POSIX shell (macOS, Linux, or WSL)

---

## Backend — installation & run

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Optional: copy environment template
cp .env.example .env

# Initialise the SQLite schema and load sample data
python -m app.seed

# Start the API
uvicorn app.main:app --reload --port 8000
```

The seed is idempotent: it loads a small editorial corpus the first
time, and reports `Seed skipped` on subsequent runs.

### Tests

```bash
pip install -r requirements-dev.txt
pytest
```

The suite covers entity identity, timestamps, enum persistence,
relationship integrity, and uniqueness constraints against an
in-memory SQLite database.

The API is then reachable at:

- `http://127.0.0.1:8000/`            — service identity
- `http://127.0.0.1:8000/api/health`  — liveness probe
- `http://127.0.0.1:8000/api/meta`    — application metadata
- `http://127.0.0.1:8000/docs`        — interactive OpenAPI documentation

### Switching to PostgreSQL

The database layer is engine-agnostic. To migrate, set:

```env
DATABASE_URL=postgresql+psycopg://user:password@host:5432/logosforge
```

in `backend/.env` and install the relevant driver
(e.g. `pip install psycopg[binary]`). No code changes are required.

---

## Frontend — installation & run

```bash
cd frontend
npm install
npm run dev
```

The dashboard is then reachable at `http://127.0.0.1:5173/`.
Vite proxies `/api/*` to `http://127.0.0.1:8000` during development,
so the backend should be running in parallel.

### Production build

```bash
npm run build      # type-check + bundle to ./dist
npm run preview    # serve the built bundle locally
```

---

## Design language

- Minimal. Professional. Editorial. Archival.
- Dark surfaces (`ink-800`) with parchment-toned type.
- Serif display (EB Garamond / Cormorant), monospace for metadata,
  sans-serif for body.
- No SaaS gradients, no startup ornament.

---

## Domain model

The editorial schema is populated by `app.models` and materialised into
SQLite (or PostgreSQL) by `init_db()`.

### Entities

| Entity            | Purpose                                                                                  |
| ----------------- | ---------------------------------------------------------------------------------------- |
| `User`            | Staff account (editor, copy editor, proofreader, designer, production manager, admin).   |
| `Author`          | External contributor; distinct from staff `User`.                                        |
| `Manuscript`      | The work itself, carrying a current workflow status and metadata.                        |
| `Review`          | A reader's verdict on a manuscript (`accept` / `reject` / `revise`) with optional rating.|
| `WorkflowEvent`   | Append-only timeline of status transitions for a manuscript.                             |
| `Contract`        | Agreement between an `Author` and the house for a given `Manuscript`.                    |
| `ProductionItem`  | A unit of production work — layout, cover design, prepress, printing.                    |
| `EditorialNote`   | Free-form note attached to a manuscript by a staff member.                               |

Every entity inherits a `BaseEntity` mixin providing:

- a UUID4 `id` (string, 36 chars — portable across SQLite and PostgreSQL),
- `created_at`,
- `updated_at` (auto-updated on every write via SQLAlchemy `onupdate`).

### Relationships

```
Author 1—* Manuscript
Author 1—* Contract
User   1—* Review            (reviewer)
User   1—* WorkflowEvent     (actor, nullable)
User   1—* EditorialNote     (author_user)
User   1—* ProductionItem    (assignee, nullable)

Manuscript 1—* Review
Manuscript 1—* WorkflowEvent
Manuscript 1—* Contract
Manuscript 1—* ProductionItem
Manuscript 1—* EditorialNote
```

### Workflow statuses

`Submitted → Under Review → Accepted | Rejected → Development Editing → Copy Editing → Proofreading → Layout → Cover Design → Prepress → Published → Archived`

All statuses are exposed as the `WorkflowStatus` enum and stored
as strings in the database for human-readable inspection and
PostgreSQL forward-compatibility.

### Other enums

`UserRole`, `ReviewVerdict`, `ContractStatus`, `ProductionStage`,
`ProductionItemStatus`, `EditorialNoteKind`.

---

## Status

Schema complete. HTTP endpoints currently expose `health` and `meta`;
routers for the editorial entities will be added in the next edition.
