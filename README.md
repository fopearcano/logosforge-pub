# LOGOSFORGE

A local-first editorial management platform for publishing houses.
LOGOSFORGE is intended as a quiet, archival workspace for the daily
ledger of a press — manuscripts, authors, contracts, and production —
under a single, refined surface.

This repository contains the foundation only. Domain logic (catalogue,
manuscripts, authors, production, archive) will follow in successive
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
    seed.py        Schema initialisation entrypoint
    models/        SQLModel domain entities
    routers/       HTTP routers (health, meta, …)
    services/      Business logic
    schemas/       Request/response payloads
    utils/         Cross-cutting helpers

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

# Initialise the SQLite schema
python -m app.seed

# Start the API
uvicorn app.main:app --reload --port 8000
```

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

## Status

Foundation only. The schema is empty; routers expose only `health` and
`meta`. Subsequent editions will introduce the catalogue, manuscript
workflow, author dossiers, contracts, and production scheduling.
