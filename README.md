# LOGOSFORGE

A local-first editorial management platform for publishing houses.
LOGOSFORGE is intended as a quiet, archival workspace for the daily
ledger of a press — manuscripts, authors, contracts, and production —
under a single, refined surface.

This repository contains the foundation, the editorial domain schema,
a full CRUD HTTP API, and JWT-based authentication with role-based
access control. UI for the domain entities will follow in successive
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
    auth/          Password hashing, JWT, DI dependencies
    models/        SQLModel domain entities + enums
    routers/       HTTP routers (auth, health, meta, …)
    services/      Business logic
    schemas/       Request/response payloads
    utils/         Cross-cutting helpers
  tests/           Pytest suite (model + router + auth)

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
- `http://127.0.0.1:8000/api/...`     — editorial CRUD (see [API surface](#api-surface))
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
| `User`            | Staff account with a role (see [Authentication](#authentication)).                       |
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

## Authentication

LOGOSFORGE uses JWT bearer tokens, OAuth2 password flow, and a
role-based access dependency chain.

### Roles

| Role                 | Notes                                                          |
| -------------------- | -------------------------------------------------------------- |
| `admin`              | Full access, including all destructive endpoints.              |
| `editor`             | Editorial reads and writes; cannot delete.                     |
| `reviewer`           | Submits reviews; otherwise read-only on the editorial graph.   |
| `production_manager` | Drives `ProductionItem` and post-acceptance workflow.          |
| `marketing`          | Read-only access geared toward catalogue/promotion data.       |
| `archive_reader`     | Read-only access intended for the archive view.                |

The role set lives in `app.models.enums.UserRole` and is exposed on every
token issued by `/api/auth/login`.

### Access policy

| Verb                    | Requirement                                  |
| ----------------------- | -------------------------------------------- |
| `GET /api/...`          | Public (anonymous reads).                    |
| `POST` and `PATCH /api/...` | Any authenticated user.                  |
| `DELETE /api/...`       | `admin` role only.                           |
| `GET /api/auth/me`      | Any authenticated user.                      |

Reusable dependency objects live in `app.auth`: `AUTHED` and `ADMIN_ONLY`
are passed to FastAPI route decorators via `dependencies=...`. The
factory `require_role(UserRole.X, UserRole.Y, ...)` builds custom
guards for future endpoints.

### Endpoints

```
POST /api/auth/login    OAuth2 password flow (form-encoded: username, password)
GET  /api/auth/me       Returns the current authenticated user
```

`POST /api/auth/login` accepts standard form-encoded fields
(`username`, `password`) — the `username` is the user's email — and
returns:

```json
{
  "access_token": "...",
  "token_type": "bearer",
  "expires_at": "2026-05-14T07:41:50+00:00",
  "user": { "id": "...", "email": "...", "full_name": "...", "role": "admin", "is_active": true }
}
```

Send the token on subsequent requests as `Authorization: Bearer <token>`.

### Demo credentials

After running `python -m app.seed`, every seeded user has the password
`logosforge`. Use any of:

| Email                                       | Role                 |
| ------------------------------------------- | -------------------- |
| `helena.pryce@logosforge.local`             | `admin`              |
| `jonas.marten@logosforge.local`             | `editor`             |
| `cecilia.dore@logosforge.local`             | `editor`             |
| `tomas.aribau@logosforge.local`             | `editor`             |
| `ruth.engstrom@logosforge.local`            | `editor`             |
| `bartholomew.krause@logosforge.local`       | `reviewer`           |
| `kazu.fujita@logosforge.local`              | `production_manager` |
| `ines.harlan@logosforge.local`              | `production_manager` |
| `mireille.vance@logosforge.local`           | `marketing`          |
| `olesya.kestral@logosforge.local`           | `archive_reader`     |

Example login:

```bash
curl -X POST http://127.0.0.1:8000/api/auth/login \
  -d 'username=helena.pryce@logosforge.local&password=logosforge'
```

### Configuration

Set the following in `backend/.env` for any non-development deployment:

```env
SECRET_KEY=<long-random-secret>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

The shipped dev default is obviously insecure and is intentionally
visible in the codebase. Authentication is a foundation only — no
refresh tokens, no rate limiting, no password rotation, no audit log.

---

## API surface

All endpoints live under `/api`, are documented at `/docs`, and return
JSON. Every list endpoint returns a paginated envelope:

```json
{
  "items": [ /* ... */ ],
  "total": 42,
  "skip": 0,
  "limit": 50
}
```

`skip` defaults to `0`, `limit` defaults to `50` (max `200`).

### Resources

| Resource         | Path                       |
| ---------------- | -------------------------- |
| Authors          | `/api/authors`             |
| Manuscripts      | `/api/manuscripts`         |
| Reviews          | `/api/reviews`             |
| Workflow events  | `/api/workflow-events`     |
| Contracts        | `/api/contracts`           |
| Production items | `/api/production-items`    |
| Editorial notes  | `/api/editorial-notes`     |

Each resource exposes the same five verbs:

| Method   | Path             | Description                  | Status |
| -------- | ---------------- | ---------------------------- | ------ |
| `GET`    | `/{resource}`    | List (paginated, filterable) | 200    |
| `GET`    | `/{resource}/{id}` | Read one                   | 200 / 404 |
| `POST`   | `/{resource}`    | Create                       | 201 / 404 / 422 |
| `PATCH`  | `/{resource}/{id}` | Partial update             | 200 / 404 / 422 |
| `DELETE` | `/{resource}/{id}` | Remove                     | 204 / 404 |

### Filters

| Endpoint                  | Query parameters                                              |
| ------------------------- | ------------------------------------------------------------- |
| `/api/manuscripts`        | `status`, `genre`, `author_id`                                |
| `/api/reviews`            | `manuscript_id`, `reviewer_id`                                |
| `/api/workflow-events`    | `manuscript_id`                                               |
| `/api/contracts`          | `manuscript_id`, `author_id`, `status`                        |
| `/api/production-items`   | `manuscript_id`, `assignee_id`, `stage`, `status`             |
| `/api/editorial-notes`    | `manuscript_id`, `author_user_id`, `kind`, `pinned`           |

All list endpoints additionally accept `skip` and `limit`.

### Error model

| Status | Meaning                                                       |
| ------ | ------------------------------------------------------------- |
| `401`  | Missing, invalid, or expired bearer token.                    |
| `403`  | Authenticated, but the role is not permitted.                 |
| `404`  | Entity not found, including missing FK references on `POST`.  |
| `409`  | Database constraint violation (uniqueness, FK race).          |
| `422`  | Request payload failed validation.                            |

---

## Status

Schema complete, CRUD complete, authentication and RBAC scaffolding in
place. `User` management endpoints (CRUD, password rotation, invites)
and the UI for the editorial entities will follow in subsequent
editions.
