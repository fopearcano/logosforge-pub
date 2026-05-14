# LOGOSFORGE

A local-first editorial management platform for publishing houses.
LOGOSFORGE is intended as a quiet, archival workspace for the daily
ledger of a press — manuscripts, authors, contracts, and production —
under a single, refined surface.

This repository contains the foundation, the editorial domain schema,
a full CRUD HTTP API, JWT-based authentication with role-based access
control, an editorial workflow engine, a full manuscript detail page,
an expanded dashboard, a cross-entity search engine with filters, a
dedicated read-only archive view, a production management module,
attachment + export systems (Markdown / JSON, with PDF reserved),
structured logging with per-request correlation, sortable list
endpoints, a Postgres-ready Docker Compose stack, AI integration
scaffolding (OpenAI / OpenRouter / LM Studio compatible, with a
dry-run default), and a small editorial knowledge graph (typed
entities, relationships, and manuscript ↔ entity links) — all wired
through to a dark-themed React UI with inline editing.

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

The register is **literary, archival, slightly monastic** — closer to a
print broadsheet than a SaaS dashboard.

### Palette

The Tailwind theme is restricted to a small, deliberately drab set:

| Token            | Use                                                   |
| ---------------- | ----------------------------------------------------- |
| `ink-800`        | Page background                                       |
| `ink-700` / `650`| Elevated surfaces (table-row hover, ledger cells)     |
| `ink-900`        | Footer / deepest declaration                          |
| `parchment`      | Body text                                             |
| `parchment-muted`| Secondary copy                                        |
| `parchment-dim`  | Eyebrow / mono labels                                 |
| `rule`           | Hairline borders, table dividers, focus underlines    |
| `accent`         | Antique brass — used only for active state and focus  |
| `accent.soft`    | Selection and accent hover-fill                       |
| `signal`         | Muted oxblood for overdue, blocked, reject, errors    |

No bright blues or greens. No gradients. The only colour intensity is
`accent` (warm brass) and `signal` (dusty oxblood); both are pulled
toward parchment so they never feel like alerts on a SaaS console.

### Typography

- Serif display: EB Garamond / Cormorant Garamond, with old-style
  numerals (`onum`), ligatures, and tight (-0.012em) tracking on
  headings.
- Monospace: JetBrains Mono / IBM Plex Mono, used for eyebrows,
  metadata, table column heads, status pills, and call numbers.
- Sans-serif: Inter, reserved for the chrome (header, footer, nav).
- Long-form prose uses the `.editorial-prose` utility: 1.7 leading,
  serif, parchment at 90% — a chronicle cadence rather than a UI one.
- A small set of reusable utilities (`.label-eyebrow`,
  `.editorial-rule`, `.nav-link`, `.nav-link-active`, `.field-input`,
  `.field-select`, `.field-mono`, `.button-quiet`, `.button-accent`,
  `.row-clickable`) keeps the surface consistent across pages.

### Rules and ornament

- Hairline rules everywhere. No box shadows, no rounded corners on
  primary surfaces (status pills are the only square-cornered chips
  in the system).
- Active navigation links are marked by a 1px brass underline below
  the label, not by a fill.
- Long lists are separated by horizontal rules rather than cards.
- Focus state is a single accent border-bottom on form fields; no
  browser glow.

### Avoided

- Bright startup primaries, gradients, neon accents.
- Playful icons, illustrations, mascots.
- Drop shadows, glassmorphism, gradients-on-borders.
- Over-saturation. The only deviation is the `accent` brass, kept to
  a single highlight per surface.

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

## Attachments and exports

### Attachment metadata

`Attachment` records sit alongside the manuscript and capture every
file an editorial house wants tracked, whether or not the bytes
themselves are on disk yet.

```
id, manuscript_id, uploader_id,
filename, content_type, size_bytes,
kind         (manuscript_draft · editor_marked_copy · cover_artwork
              · proof · contract_scan · other),
storage_key,                  # opaque handle; "placeholder:…" for stubs
sha256, description,
created_at, updated_at
```

Two write paths share a single model:

| Mode          | When                                                                   |
| ------------- | ---------------------------------------------------------------------- |
| **Placeholder** | `POST /api/attachments` (JSON) — records that a file is expected but no bytes are on disk. `storage_key` is set to `placeholder:<uuid>`. |
| **Real upload** | `POST /api/attachments/upload` (multipart) — streams bytes through the storage backend, records the resulting `size_bytes` and `sha256`. |

Both paths require authentication; DELETE is admin-only.

### Local storage architecture

The storage layer is a small backend abstraction:

```
backend/app/services/storage.py
  ├── safe_filename(name)       # slug-clean a user-supplied filename
  ├── LocalFileStorage(root)
  │     ├── path_for(key)
  │     ├── exists(key)
  │     ├── write(key, stream)  → StoredFile(storage_key, size, sha256)
  │     └── delete(key)
  └── get_storage()             # module-level singleton from settings
```

The root directory is configured via the `STORAGE_PATH` env var (see
`.env.example`); it defaults to `backend/storage/`. The directory is
gitignored. To swap in S3, MinIO, or another backend, implement the
same interface and replace what `get_storage()` returns — the
attachments router never reaches past the abstraction.

Tests use pytest's `tmp_path` and monkeypatch the cached backend to a
temporary directory, so the real disk is never touched.

### Attachment endpoints

```
GET    /api/attachments                       list (paginated, filter by manuscript_id, kind)
GET    /api/attachments/{id}                  fetch metadata
POST   /api/attachments                       placeholder create  (auth)
POST   /api/attachments/upload                multipart upload   (auth)
PATCH  /api/attachments/{id}                  edit kind/description/filename (auth)
DELETE /api/attachments/{id}                  remove + delete bytes (admin)
GET    /api/attachments/{id}/download         stream bytes; 410 for placeholders
```

### Exports

Manuscript exports live behind a small registry so a future PDF
exporter can be wired in by registering an `Exporter` for
`ExportFormat.PDF` — no changes to the route are required.

```
backend/app/services/exports/
  ├── base.py                # Exporter protocol + ManuscriptExportBundle
  ├── bundle.py              # build_bundle(session, manuscript_id)
  ├── markdown_export.py     # MarkdownExporter
  ├── json_export.py         # JSONExporter
  └── __init__.py            # EXPORTERS registry  → ExportFormat → Exporter
```

Every exporter consumes the same bundle: the manuscript and author,
plus the full workflow chronicle, every review, and every editorial
note. The endpoint dispatches on `?format=`:

```
GET /api/manuscripts/{id}/export?format=markdown   →  200 text/markdown
GET /api/manuscripts/{id}/export?format=json       →  200 application/json
GET /api/manuscripts/{id}/export?format=pdf        →  501 Not Implemented
GET /api/exports/formats                           →  list of supported formats
```

Responses include a `Content-Disposition: attachment; filename="<slug>.<ext>"`
header so browsers offer a file download.

#### Markdown shape

```
# {title}
## _{subtitle}_

> {author} · {country}

## Metadata
| Field | Value | …

## Synopsis
{prose}

## Workflow chronicle
| When | From | To | By | Note |

## Reviews
### {verdict} · {rating}/5 · {reviewer}
{summary}

## Editorial notes
### {kind} · 📌 Pinned · {author}
{body}
```

#### JSON shape

```
{
  "exported_at": "<iso datetime>",
  "schema_version": 1,
  "manuscript": { … },
  "author":     { … } | null,
  "workflow_history": [ … ],
  "reviews":         [ … ],
  "editorial_notes": [ … ]
}
```

`schema_version` lets future archives detect the layout they're
parsing without sniffing field shapes.

### Frontend touchpoints

- **`AttachmentsPanel`** (manuscript-view sidebar) — lists attachments
  with filename, kind, size, uploader, and creation date; "Placeholder"
  chip when there are no bytes. A "Record a file…" form below the list
  posts the placeholder record. Disabled when the manuscript is in
  the archive read-only state.
- **`ExportMenu`** (manuscript-view header) — two anchor links that
  hit the export endpoint with the appropriate `?format=`; the
  browser receives the file via Content-Disposition. A third tile
  shows `PDF · soon` as a registered-but-not-implemented placeholder.

---

## Operations

### Sortable list endpoints

The two largest collections accept `sort_by` and `sort_dir` query
parameters. Unknown values return 422 (Pydantic-enforced).

| Endpoint            | `sort_by`                                            | Default      |
| ------------------- | ---------------------------------------------------- | ------------ |
| `/api/manuscripts`  | `title`, `status`, `genre`, `created_at`, `updated_at` | `created_at` desc |
| `/api/authors`      | `full_name`, `country`, `created_at`                  | `full_name` asc   |

### Logging and correlation

A small middleware (`app/utils/middleware.py`) stamps every request
with an `X-Request-ID` (passing through any inbound id from upstream).
The id is bound to a `ContextVar`, so every log line emitted while
that request is in flight carries the same `rid=` field — including
the line written by the global access middleware:

```
2026-05-14 09:32:11 [INFO ] app.access rid=4be207b6-… GET /api/manuscripts → 200 · 11.4ms
```

Two error paths return the request id in the response body, too, so
you can grep your logs from a curl trace:

| Trigger                          | Status | Body                                                |
| -------------------------------- | ------ | --------------------------------------------------- |
| `IntegrityError` (FK / unique)   | `409`  | `{"detail": "Database constraint violation.", "request_id": "…"}` |
| Unhandled exception              | `500`  | `{"detail": "Internal server error.", "request_id": "…"}` |

Other handlers (404, 422, 401, 403) keep their default FastAPI
shape; they all carry the `X-Request-ID` header via the middleware.

`LOG_LEVEL` (default `INFO`) is the single setting that controls the
loggers — uvicorn's per-request access log is silenced in favour of
the middleware-emitted line so output stays single-source.

### Test suite

```
backend/tests/
  conftest.py                  fixtures: engine, session, anon_client,
                               client (admin), editor_client, tokens
  test_models.py               schema + relationship + uniqueness
  test_routers.py              CRUD lifecycle + filters + pagination envelope
  test_auth.py                 login / me / role gating
  test_dashboard.py            dashboard summary endpoints
  test_search.py               cross-entity search + filters
  test_production_records.py   production-record CRUD + by-manuscript lookup
  test_attachments.py          placeholder + multipart upload + download
  test_exports.py              markdown / json bodies + PDF 501
  test_workflow_service.py     pure-Python tests for app.services.workflow
  test_validation.py           Pydantic bound checks across resources
  test_pagination_sorting.py   skip / limit edges + sort_by / sort_dir
  test_request_id.py           X-Request-ID minted, passed through, on errors
```

```bash
cd backend
.venv/bin/python -m pytest -q
```

The full suite runs in roughly 30 seconds against an in-memory
SQLite engine (single-connection `StaticPool` so writes from a test
fixture are visible to subsequent client requests).

### Docker Compose

```bash
cp .env.example .env
docker compose up --build
```

The stack lifts:

| Service    | Image / build         | Default port |
| ---------- | --------------------- | ------------ |
| `postgres` | `postgres:16-alpine`  | `5432`       |
| `backend`  | `./backend/Dockerfile` (FastAPI + Uvicorn, with `psycopg[binary]`) | `8000` |
| `frontend` | `./frontend/Dockerfile` (multi-stage Vite build → nginx) | `8080` |

`postgres_data` and `storage` are named volumes so manuscript files
and the database persist across container restarts. Backend
`DATABASE_URL` is wired automatically; the frontend's nginx proxies
`/api/` to the backend service so a single origin serves both.

### PostgreSQL compatibility

The codebase has been Postgres-ready since the foundation — the
SQLAlchemy URL is the only switch:

```env
# backend/.env (or in your compose .env)
DATABASE_URL=postgresql+psycopg://user:password@host:5432/logosforge
```

`backend/requirements-postgres.txt` adds the driver:

```bash
pip install -r backend/requirements-postgres.txt
```

The SQLite-only quirks (`PRAGMA foreign_keys=ON`,
`check_same_thread`) are gated on the URL prefix, so no other code
needs changing. The backend Dockerfile installs the Postgres driver
unconditionally so the same image serves either backend.

### Backup placeholders

`scripts/backup.sh` and `scripts/restore.sh` ship as starting points
for an off-site backup pipeline. `backup.sh` detects whether the
configured database is SQLite or PostgreSQL and writes a timestamped,
gzipped dump under `$BACKUP_DIR` (default `./backups`); it also
archives the attachment storage tree so a restored database lines up
with the files it references. `restore.sh` accepts a single backup
file and dispatches on extension (`*.sql.gz` → `psql`, `*.sqlite.gz`
→ overwrite, `*.tar.gz` → extract).

```bash
DATABASE_URL=postgresql+psycopg://… ./scripts/backup.sh
./scripts/restore.sh backups/db-20260514T093000Z.sql.gz
```

These are intentionally unmanaged — wire in your own retention,
encryption, off-site copy, and verification before relying on them.

---

## AI integration

A small abstraction layer prepares the system for AI-assisted editorial
workflows. The actual analytical work is intentionally light — the
foundation is the **provider layer**, the **feature registry**, and the
**persistence surface**.

### Provider abstraction

```
app/services/ai/providers/
  ├── base.py           Protocol — LLMProvider, ChatMessage, CompletionResult
  ├── dry_run.py        DryRunProvider — canned, deterministic, no network
  ├── openai_compat.py  OpenAICompatibleProvider — POST /v1/chat/completions
  └── registry.py       get_provider(), reset_provider_cache()
```

`OpenAICompatibleProvider` is enough for everything in the
foundation's matrix — it's the same wire format for OpenAI itself,
OpenRouter, LM Studio, llama.cpp's server, and Ollama running its
OpenAI shim. The registry picks one of:

| `AI_PROVIDER` | Default base URL                                | Use                |
| ------------- | ----------------------------------------------- | ------------------ |
| `dry_run`     | —                                               | Default; canned    |
| `openai`      | `https://api.openai.com/v1`                     | Hosted             |
| `openrouter`  | `https://openrouter.ai/api/v1`                  | Multi-model router |
| `lm_studio`   | `http://localhost:1234/v1`                      | Local LM Studio    |
| `openai_compatible` | (set `AI_BASE_URL` explicitly)            | Anything else      |

Configuration (`backend/.env`):

```env
AI_PROVIDER=lm_studio
AI_BASE_URL=http://localhost:1234/v1     # optional; defaults above
AI_API_KEY=                              # if the backend requires one
AI_MODEL=qwen2.5-14b-instruct
AI_REQUEST_TIMEOUT=60
```

The dry-run provider ships **canned, feature-aware JSON** so every
feature, endpoint, and UI panel works end-to-end without leaving the
process. It is the default in development, in tests, and whenever
`AI_PROVIDER` is unset.

### Features

```
app/services/ai/features/
  ├── summarize.py              SummaryResult           one-line · summary · themes
  ├── style_analysis.py         StyleAnalysisResult     register · voice · rhythm · concerns
  ├── editorial_suggestions.py  EditorialSuggestions    [{kind, title, rationale}]
  ├── semantic_tags.py          SemanticTagsResult      [tags]
  └── consistency.py            ConsistencyCheckResult  [{kind, where, description}]
```

Every feature is a small function:

```
run_<feature>(bundle, provider) -> <FeatureResult>
```

— builds a JSON-oriented prompt from a shared `manuscript_excerpt`
helper, calls the provider, and runs a permissive JSON parser
(`parse_json_object`) that tolerates prose around the JSON object.
The router dispatches generically via a registry:

```python
FEATURES: dict[AIFeature, Callable] = {
    AIFeature.SUMMARIZE: run_summarize,
    AIFeature.STYLE_ANALYSIS: run_style_analysis,
    AIFeature.EDITORIAL_SUGGESTIONS: run_editorial_suggestions,
    AIFeature.SEMANTIC_TAGS: run_semantic_tags,
    AIFeature.CONSISTENCY_CHECK: run_consistency_check,
}
```

Adding a sixth feature is a new file plus a one-line registration.

### Endpoints

```
POST /api/ai/manuscripts/{id}/summarize              auth
POST /api/ai/manuscripts/{id}/style-analysis         auth
POST /api/ai/manuscripts/{id}/editorial-suggestions  auth
POST /api/ai/manuscripts/{id}/semantic-tags          auth
POST /api/ai/manuscripts/{id}/consistency-check      auth

GET  /api/ai/manuscripts/{id}/insights[?feature=…]   public read
DELETE /api/ai/insights/{id}                         auth

GET  /api/ai/providers                               public read; reports
                                                     the active backend +
                                                     known list
```

Each `POST` returns:

```json
{
  "feature": "summarize",
  "provider": "dry_run",
  "model": "stub",
  "generated_at": "2026-05-14T10:39:11+00:00",
  "insight_id": "78b584e4-…",
  "result": { "one_line": "…", "summary": "…", "themes": ["…"] }
}
```

### Persistence

Every run inserts an `AIInsight` row:

```
ai_insights:
  id, manuscript_id (FK), feature (enum), provider, model,
  payload (JSON-encoded text), created_at, updated_at
```

This gives the UI a cached "last run" per (manuscript, feature) to
display without re-running the model, plus a primitive audit trail.
The `GET /api/ai/manuscripts/{id}/insights` endpoint returns them
newest-first, filterable by `feature`.

### Frontend touchpoint

The manuscript-view sidebar gains an `AIPanel` section. It calls
`/api/ai/providers` on mount to label whether the backend is live or
dry-run, fetches the cached `AIInsight`s for the manuscript, and
shows each feature as a row with a "Run" / "Re-run" button. Expanding
a row renders the raw `result` as monospace JSON — a deliberately
unstyled view, since the meaningful display surface per feature is
work for the next iteration.

The panel disables Run when the manuscript is in the archive
read-only state, matching the rest of the page's vocabulary.

---

## Knowledge system

A small editorial knowledge graph sits beside the manuscript table.
Inspired by the PSYKE pattern of typed nodes, typed edges, and
contextual link-tables, it gives the house a single place to record
the themes, motifs, places, and people that recur across the
catalogue — and the threads that connect them.

### Model

```
knowledge_entities         knowledge_relationships          manuscript_entity_links
  id  (uuid)                 id                                id
  kind  (EntityKind)         source_id   FK → entities         manuscript_id  FK → manuscripts
  name                       target_id   FK → entities         entity_id       FK → entities
  slug   (unique)            kind  (RelationshipKind)          role  (ManuscriptLinkRole)
  description                weight  (0–1)                     relevance  (0–1)
  extras (JSON-text)         description                       notes
```

The three enums are open enough to cover most editorial needs and
fall through to `other` when in doubt:

| Enum                  | Values                                                                            |
| --------------------- | --------------------------------------------------------------------------------- |
| `EntityKind`          | `character`, `place`, `theme`, `motif`, `organization`, `work`, `person`, `period`, `other` |
| `RelationshipKind`    | `related_to`, `influences`, `descends_from`, `contrasts_with`, `inhabits`, `authored`, `part_of`, `sibling_of`, `mentor_of`, `adapts`, `other` |
| `ManuscriptLinkRole`  | `tagged`, `features`, `references`, `set_in`, `derived_from`, `other`             |

A *narrative tag* is just a `KnowledgeEntity` of an appropriate kind
(`theme` / `motif` / `period`…) linked via a `ManuscriptEntityLink`
with role `tagged`. The graph stays uniform; the UI groups by role.

### Service layer

```
app/services/knowledge.py
  ├── slugify(value)                      # stable URL-safe identifiers
  └── neighborhood(session, root_id,      # BFS outward through typed edges,
                   *, depth=1, limit=200) #   capped at `limit` nodes
```

The `_resolve_slug` helper auto-disambiguates derived slugs (`memory`,
`memory-2`, `memory-3`…), so seeding adjacent entities never produces
a 409. An explicit slug is honoured verbatim and clashes return 409.

### Endpoints

```
GET    /api/knowledge/entities             list (filter by kind, q)
GET    /api/knowledge/entities/{id}        fetch by id
GET    /api/knowledge/entities/by-slug/{s} fetch by slug
POST   /api/knowledge/entities             create (auth)
PATCH  /api/knowledge/entities/{id}        update (auth)
DELETE /api/knowledge/entities/{id}        cascade delete (admin)

GET    /api/knowledge/entities/{id}/neighborhood?depth=1..4
GET    /api/knowledge/entities/{id}/manuscripts

GET    /api/knowledge/relationships        list (filter by endpoints / kind)
GET    /api/knowledge/relationships/{id}   detail with endpoint names
POST   /api/knowledge/relationships        create (auth)
PATCH  /api/knowledge/relationships/{id}   update (auth)
DELETE /api/knowledge/relationships/{id}   remove (auth)

GET    /api/manuscripts/{id}/entity-links               list (filter by role)
POST   /api/manuscripts/{id}/entity-links               create (auth)
PATCH  /api/manuscripts/{id}/entity-links/{link_id}     update (auth)
DELETE /api/manuscripts/{id}/entity-links/{link_id}     remove (auth)
```

Entity deletion runs an explicit cascade in app code (relationships
on either side and manuscript links touching the entity are removed
before the entity itself) so the behaviour is identical on SQLite
and PostgreSQL.

Self-loop relationships are refused with 409. Both endpoints of a
relationship must exist or the create returns 404. The neighborhood
endpoint walks outward at the requested depth (1–4) and only keeps
edges whose endpoints both survived the node-limit truncation, so a
truncated graph stays coherent.

### Seed corpus

`python -m app.seed` populates a small starter graph the five demo
manuscripts can hang off:

- **Themes**: Inland seas, Memory, Labour, Letters, Archive
- **Motifs**: Salt, Type design
- **Places**: Iberian peninsula, Kyoto
- **Periods**: Early twentieth century
- **People**: Georges-Louis Leclerc de Buffon

with five typed edges between them (`Inland seas → Salt`,
`Letters → Memory`, `Archive → Memory`, `Type design → Labour`,
`Buffon → Archive (influences)`) and fifteen-odd manuscript links
covering every demo manuscript.

### Frontend touchpoints

- **`SemanticPanel`** — manuscript-view sidebar section. Lists the
  manuscript's entity links grouped by role, as monospace chips
  (`Tagged`, `Set in`, `Features`, `References`, `Derived from`,
  `Other`). Each chip carries an `×` to remove the link. A footer
  form lets the user pick from existing entities and a role to add
  a new link. The whole panel disables in the archive read-only
  mode.
- **`RelationshipPreview`** — a small text-mode placeholder for the
  graph view. Tapping any chip in the `SemanticPanel` expands the
  preview below: an arrowed list of the entity's first-hop
  neighbours, by edge kind. Direction (→ out, ← in) and the typed
  edge label both render in mono small caps, so the structure reads
  like a library card.

### Why not draw the graph

A real network visualisation is reserved for later — D3 / Cytoscape /
Sigma are easy to bolt on once the data is solid. The current
text-mode preview keeps the foundation honest about what's modelled
versus what's rendered, and matches the library-register tone the
rest of the UI is set in.

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
a read-only archive view, the production management module, the
attachment + export systems (Markdown · JSON · PDF reserved), the
AI integration scaffolding (dry-run default; OpenAI / OpenRouter /
LM Studio compatible), the editorial knowledge graph (entities,
relationships, manuscript links, neighborhood traversal), structured
logging with request-id correlation, sortable list endpoints, a
Postgres-ready Docker Compose stack, and backup placeholders are all
in place. **162** pytest cases pass. Still to come: `User`
management endpoints (CRUD, password rotation, invites), the
remaining editorial views (authors index, contracts index), the PDF
exporter itself, per-feature renderings for the AI panel, and a
proper graph-visualisation pass over the knowledge layer.
