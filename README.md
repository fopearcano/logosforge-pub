# LOGOSFORGE

A local-first editorial management platform for publishing houses.
LOGOSFORGE is intended as a quiet, archival workspace for the daily
ledger of a press — manuscripts, authors, contracts, and production —
under a single, refined surface.

This repository contains the foundation, the editorial domain schema,
a full CRUD HTTP API, JWT-based authentication with role-based access
control, an editorial workflow engine, a full manuscript detail page,
an expanded dashboard, a cross-entity search engine with filters, a
dedicated read-only archive view, and a production management module
(per-title production records, a board, a release calendar, and
production item detail pages) — all wired through to a dark-themed
React UI with inline editing.

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
manuscript opens its full detail page — see [Manuscript detail page](#manuscript-detail-page).

---

## Manuscript detail page

`ManuscriptView` is a two-column editorial detail page composed of
small, single-purpose React components.

### Layout

```
Header (title, subtitle, badge, author, word count, language)
─────────────────────────────────────────────────────────────
Synopsis (inline editable)

┌──────────────────────────────┬───────────────────────────┐
│ Workflow chronicle (timeline)│ Metadata (inline editable)│
│                              │ Author                    │
│ Editorial notes              │ Workflow control          │
│  · pinned-first list         │ Contracts                 │
│  · "Leave a note" form       │ Production                │
│                              │ Manuscript files          │
│ Reviews (read-only)          │  · placeholder            │
└──────────────────────────────┴───────────────────────────┘
```

The two-column grid collapses to a single stacked column on small
viewports.

### Sections and data sources

| Section                  | Endpoint                                  |
| ------------------------ | ----------------------------------------- |
| Header + Synopsis        | `GET /api/manuscripts/{id}`               |
| Metadata + inline edits  | `PATCH /api/manuscripts/{id}`             |
| Author                   | `GET /api/authors/{id}`                   |
| Workflow timeline        | `GET /api/manuscripts/{id}/workflow-events` |
| Transition control       | `POST /api/manuscripts/{id}/transition`   |
| Reviews                  | `GET /api/reviews?manuscript_id=…`        |
| Contracts                | `GET /api/contracts?manuscript_id=…`      |
| Production               | `GET /api/production-items?manuscript_id=…` |
| Editorial notes (list)   | `GET /api/editorial-notes?manuscript_id=…`|
| Editorial notes (create) | `POST /api/editorial-notes`               |
| Manuscript files         | UI placeholder — not yet implemented      |

Reviews, editorial notes, production items, and workflow events all
denormalise the related user's name (`reviewer_name`, `author_user_name`,
`assignee_name`, `actor_name`) so the UI can render people-readable
attribution without an additional user lookup.

### Inline editing

`EditableField` turns the title, subtitle, synopsis, genre, language,
and word count into click-to-edit fields. Hovering shows a subtle
dotted underline; clicking opens an input or textarea with explicit
Save / Cancel controls. `Enter` saves single-line fields; `Esc`
cancels in either mode. Server-side validation errors surface inline.

The fields are disabled for anonymous visitors; signing in turns them
live. Empty strings on optional fields (subtitle, synopsis, genre)
clear the column.

### Editorial notes panel

Notes are sorted with pinned entries first, then newest. Each shows
its kind, a "Pinned" indicator when applicable, the author's name,
and timestamp. The "Leave a note" form below the list posts to
`/api/editorial-notes`; it is disabled until the user signs in.

### Attachments

Files are not yet wired through. The sidebar shows a clearly-labelled
placeholder section with disabled controls so the eventual shape of
the feature is visible in the layout.

---

## Dashboard

The dashboard composes five widgets backed by a dedicated
`/api/dashboard` router.

### Endpoints

| Method | Path                                | Returns                                                                |
| ------ | ----------------------------------- | ---------------------------------------------------------------------- |
| `GET`  | `/api/dashboard/status-counts`      | All 12 workflow statuses with their counts (zero rows included).       |
| `GET`  | `/api/dashboard/active-reviews`     | Manuscripts in `under_review` with reviewer count and latest verdict.  |
| `GET`  | `/api/dashboard/upcoming-releases`  | Manuscripts in `layout` / `cover_design` / `prepress`, closest first.  |
| `GET`  | `/api/dashboard/deadlines`          | Open `ProductionItem` rows with due dates, soonest first.              |
| `GET`  | `/api/dashboard/recent-activity`    | Recent `WorkflowEvent` rows with manuscript title and actor name.      |

All five are public reads. Each row includes the `manuscript_id` so
the UI can deep-link to the [manuscript detail page](#manuscript-detail-page).
`limit` defaults to 20 (max 100).

### Layout

```
Prospectus heading                Colophon (service, edition, env, count)
─────────────────────────────────────────────────────────────────────────
Indicator cards (4)
  · Manuscripts on the desk · Under review · In production · Overdue
─────────────────────────────────────────────────────────────────────────
Manuscripts by status (table) │ Recent workflow activity (timeline feed)
─────────────────────────────────────────────────────────────────────────
Active reviews (list)         │ Upcoming releases (table)
─────────────────────────────────────────────────────────────────────────
Deadlines (table, full width)
─────────────────────────────────────────────────────────────────────────
Manuscripts in the house (existing list)
```

The grid collapses to a single column below `lg`. Each widget loads
through the API in parallel; the indicator cards derive from the
already-fetched status counts and deadlines, so no extra endpoint
exists for them.

### Status indicators

- **Status counts**: every status renders as a row with a hairline
  rule whose length is proportional to its count and capped against
  the page maximum — a quiet bar chart in print register.
- **Recent activity**: a vertical chronicle. Each entry shows the
  manuscript (clickable), the `from → to` `StatusBadge` pair, the
  actor, and any transition note.
- **Deadlines**: relative time renders as "in N days" or "N days
  overdue" — the latter switches to the accent colour, mirrored by
  the indicator card.

---

## Search and archive

### Search

A single cross-entity search endpoint backs the reading-room page.

```
GET /api/search
    ?q=<term>                       required, min length 1
    [&status=<workflow_status>]     applies to manuscripts and parents
    [&genre=<exact>]                applies via the manuscript table
    [&year=<YYYY>]                  filters by manuscript created_at year
    [&author_id=<uuid>]             filters to a single author / their work
    [&rights_territory=<value>]     applies to contracts only
    [&limit=<1..100>]               default 20 per section
```

The query `q` is matched case-insensitively (`ILIKE %q%`) against:

| Entity            | Columns matched                                       |
| ----------------- | ----------------------------------------------------- |
| `Manuscript`      | `title`, `subtitle`, `synopsis`, `genre`              |
| `Author`          | `full_name`, `biography`, `country`                   |
| `Review`          | `summary`                                             |
| `EditorialNote`   | `body`                                                |
| `Contract`        | `terms`, `rights_territory`                           |

Reviews, notes, and contracts honour the manuscript-level filters
(`status`, `genre`, `year`, `author_id`) via a join on `manuscripts`.
The endpoint returns a grouped response:

```json
{
  "query": "europe",
  "total": 2,
  "manuscripts": [...],
  "authors": [...],
  "reviews": [...],
  "editorial_notes": [...],
  "contracts": [...]
}
```

Each hit denormalises the relevant attribution (`author_name`,
`manuscript_title`, `reviewer_name`, `author_user_name`) so the UI
needs no follow-up requests to render a useful row.

The implementation uses plain `ILIKE` with indexed FK columns. For
small-to-medium catalogues this is adequate. A future iteration could
move to SQLite FTS5 (or PostgreSQL `tsvector`) without changing the
endpoint contract.

`Contract` gained an indexed `rights_territory` column to support the
filter. Free-text (so a deployment can use `world`, `europe`,
`north_america`, `spanish_language`, etc.) with a non-exhaustive
datalist in the UI.

### Search page

`SearchPage` ships a single full-width form: a serif query input, then
five filter controls (Status select, Genre input, Year, Author select,
Rights territory text + datalist). Results render below as five
labelled sections — Catalogue · Dossier · Marginalia · Apparatus ·
Rights — each grouping hits per entity type. Empty sections display
"Nothing turned up here." inline rather than collapsing.

### Archive

`ArchivePage` reads from `GET /api/manuscripts?status=archived&limit=200`
and renders a library-card-style catalogue:

```
LF · 2024 · 8F3D1C37     The Salt Atlases               Archived · Jun 24
                         A cartography of inland seas
                         Essays · EN · 68,200 words
```

Each entry includes a small monospaced call number (`LF · <year> ·
<id-prefix>`), title and subtitle in serif, mono metadata, and the
archive date on the right. Clicking opens the manuscript detail page.

### Read-only archive mode

`ManuscriptView` checks `manuscript.status === 'archived'` and:

- shows a hairline "Archive · read-only" banner above the header;
- disables every `EditableField` (title, subtitle, synopsis, genre,
  language, word count) by passing `canEdit={false}`;
- disables the editorial-notes "Leave a note" form via the new
  `readOnly` prop on `EditorialNotesPanel`;
- relies on the workflow engine — `archived` is a terminal status,
  so the `TransitionControl` naturally has no available actions.

### Navigation

`AppShell` exposes Manuscripts (=dashboard), **Search**, and
**Archive** as live nav targets; Authors and Production remain
placeholders. `AppShell` was reshaped from a single `onHome` callback
to a generic `onNavigate(view)` callback so the four primary views
can route uniformly.

---

## Production module

The production module sits on top of two backend concerns:

| Concern               | Where it lives                                            |
| --------------------- | --------------------------------------------------------- |
| Per-title roll-up     | `ProductionRecord` (1:1 with `Manuscript`)                |
| Granular work items   | `ProductionItem` (already in the schema)                  |

### ProductionRecord

```
id, manuscript_id (unique),
isbn, release_date,
print_status, ebook_status, audiobook_status,   (formats)
cover_status, layout_status, prepress_status,    (stages)
notes,
created_at, updated_at
```

Every stream — format or stage — uses the new `StreamStatus` enum:
`not_planned`, `pending`, `in_progress`, `blocked`, `complete`. Streams
default to `not_planned` so a fresh record reflects a title that hasn't
started production work in any direction.

### Endpoints

```
GET    /api/production-records                      list (paginated)
       ?manuscript_id=<id>
       ?has_release_date=true|false
       ?release_from=YYYY-MM-DD&release_to=YYYY-MM-DD
GET    /api/production-records/{id}                 fetch one
GET    /api/production-records/by-manuscript/{mid}  fetch by manuscript (404 if none)
POST   /api/production-records                      create (auth required)
PATCH  /api/production-records/{id}                 partial update (auth required)
DELETE /api/production-records/{id}                 remove (admin only)
```

The list endpoint enriches each row with `manuscript_title`,
`manuscript_status`, and `author_name`. Results are ordered by
release date soonest first, with unscheduled records at the end.
Creation refuses a second record per manuscript (409 — the FK is
unique).

### Frontend surface

`AppShell` now exposes **Production** and **Calendar** as live nav
targets alongside Manuscripts, Search, and Archive.

| Page                  | What it does                                                       |
| --------------------- | ------------------------------------------------------------------ |
| `ProductionBoard`     | One row per production record. Title, author, manuscript status, ISBN, release, and two compact strips of `StreamStatusBadge`s — Formats and Stages. Sorted soonest-release first. |
| `ReleaseCalendar`     | Records with release dates grouped by month, with weekday + day per entry, format strip on the right. |
| `ProductionItemView`  | A single `ProductionItem`. Status (select) and due date / notes (`EditableField`) edit inline; the right sidebar shows assignment, stage, and a link back to the manuscript. The main column embeds `ProductionTimeline` highlighting the current item among its siblings. |

`StreamStatusBadge` reuses the editorial tone vocabulary (cold for
not-planned, warm for pending, live for in-progress, accent for
complete, red for blocked) so it sits naturally next to the existing
`StatusBadge`.

### Manuscript detail integration

`ManuscriptView` now embeds two production widgets in its sidebar:

- `ProductionRecordPanel` — ISBN and release date are inline-editable;
  each of the six streams (3 formats + 3 stages) has a tap-to-change
  dropdown. If no record exists yet, the panel shows a single "Open
  production record" button (sign-in gated, archive-respecting).
- `ProductionPanel` — the existing list of `ProductionItem`s, now with
  each stage row clickable. Clicking opens the `ProductionItemView`.

Both panels honour the archive read-only mode: when the manuscript is
in the `archived` status, edits and the "Open production record"
action are disabled in the same way the rest of the page is.

### Deadline tracking

The dashboard's existing **Deadlines** widget already reads from
`/api/dashboard/deadlines` (open `ProductionItem`s sorted by due
date). The new `ProductionItemView` surfaces the same "in N days" /
"N days overdue" label prominently in its section header, and
`ProductionTimeline` annotates every non-done item with the same
phrasing so a production manager has a consistent register across
the dashboard, the manuscript view, and the item detail page.

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

Schema, CRUD, authentication, the workflow engine, a full manuscript
detail page, an expanded dashboard, cross-entity search with filters,
a read-only archive view, and the production management module
(records, board, calendar, item detail) are all in place. Still to
come: `User` management endpoints (CRUD, password rotation, invites),
the remaining editorial views (authors index, contracts index), and
actual file attachment plumbing.
