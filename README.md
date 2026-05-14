# LOGOSFORGE

A local-first editorial management platform for publishing houses.
LOGOSFORGE is intended as a quiet, archival workspace for the daily
ledger of a press — manuscripts, authors, contracts, and production —
under a single, refined surface.

This repository contains the foundation, the editorial domain schema,
a full CRUD HTTP API, JWT-based authentication with role-based access
control, and an editorial workflow engine wired through to a dark-themed
React UI with a timeline and transition controls.

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

See [Workflow engine](#workflow-engine) for the transition graph,
endpoints, and UI.

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

## Workflow engine

A small state machine governs every manuscript's status. The transition
graph is the single source of truth in
`app.services.workflow.TRANSITIONS`; routers, tests, and the frontend
consume it.

### Transition graph

```
submitted          → under_review, rejected, archived
under_review       → accepted, rejected, submitted, archived
accepted           → development_editing, archived
rejected           → archived
development_editing → copy_editing, under_review, archived
copy_editing       → proofreading, development_editing, archived
proofreading       → layout, copy_editing, archived
layout             → cover_design, proofreading, archived
cover_design       → prepress, layout, archived
prepress           → published, cover_design, archived
published          → archived
archived           → (terminal)
```

Every non-terminal status can also be shelved directly to `archived`.
Backward edges allow returning a manuscript to the previous stage when
revisions are needed.

### Endpoints

| Method | Path                                                | Purpose                                |
| ------ | --------------------------------------------------- | -------------------------------------- |
| `GET`  | `/api/workflow/transitions`                         | The full transition graph.             |
| `GET`  | `/api/manuscripts/{id}/workflow-events`             | Chronological history for a manuscript.|
| `POST` | `/api/manuscripts/{id}/transition`                  | Execute a transition (authenticated).  |

`POST /api/manuscripts/{id}/transition` body:

```json
{ "to_status": "under_review", "comment": "Routing to reader." }
```

On success it records a `WorkflowEvent` with the previous status, new
status, timestamp, acting user, and comment, then returns:

```json
{
  "manuscript_id": "…",
  "status": "under_review",
  "event": { /* full WorkflowEvent including actor_name */ },
  "allowed_next": ["accepted", "archived", "rejected", "submitted"]
}
```

Disallowed transitions and self-transitions return `409` with a
descriptive `detail`. The service is exercised both directly and
through the HTTP layer in `tests/test_workflow.py`.

### Frontend

The dashboard lists every manuscript with a `StatusBadge`. Clicking a
manuscript opens its detail view, which renders:

- the manuscript header (title, author, word count, genre, language);
- a vertical `WorkflowTimeline` of every transition, with actor and
  optional comment;
- a `TransitionControl` panel — a dropdown of currently allowed
  next-states plus a comment field. The panel is disabled until the
  user signs in, and POSTs the transition through the protected
  endpoint above.

The transition control reads its options live from
`/api/workflow/transitions`, so the UI cannot drift from the
service's transition graph.

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

Schema, CRUD, authentication, and the workflow engine are in place,
with a dark editorial UI for manuscripts and transitions. Still to
come: `User` management endpoints (CRUD, password rotation, invites)
and the rest of the editorial views (authors, contracts, production
board, archive).
