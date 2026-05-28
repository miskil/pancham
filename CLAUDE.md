# CLAUDE.md — Pancham Project

## What is Pancham

Pancham is a PWA for managing village-level development programs in rural Maharashtra. It connects three actors — **Admin**, **Village**, and **Donor** — across a structured lifecycle: proposal → plan → execution → donor reporting.

Optional integration with **Bhau (भाऊ)** provides Marathi-language voice AI as a training layer for village users.

---

## Three views, three roles

| Role | Access | Description |
|---|---|---|
| `ADMIN` | Full | Onboards villages, reviews proposals and plans, moderates status updates, publishes to donor |
| `VILLAGE` | Own village only | Creates proposal, submits plan, posts status updates, responds to admin |
| `DONOR` | Read-only, curated | Sees only admin-marked villages and admin-marked status updates |

---

## Tech stack

| Layer | Choice |
|---|---|
| Frontend | React + Vite, PWA via vite-plugin-pwa |
| Styling | Tailwind CSS, mobile-first |
| Backend | FastAPI (Python 3.11+), async |
| Database | PostgreSQL on Railway |
| ORM | SQLAlchemy async + asyncpg |
| Migrations | Alembic |
| Auth | JWT, role-based (ADMIN / VILLAGE / DONOR) |
| File storage | Cloudflare R2 or Railway volume |
| Offline | Service Worker + IndexedDB queue for status posts |
| Bhau bridge | Optional REST call to Bhau FastAPI |

React functional components with hooks. No class components. State management via React Context or Zustand as needed.

---

## Village stage tracker — shared component

Both Admin view and Village view (and Donor view) show a **VillageStageTracker** at the top. It renders a horizontal 4-step stepper:

```
[ Proposal ] ——— [ Plan ] ——— [ Active ] ——— [ Completed ]
```

### Stage definitions

| Stage | Entered when |
|---|---|
| `PROPOSAL` | Village is created (onboarded by admin) |
| `PLAN` | Proposal reaches `ACCEPTED` state |
| `ACTIVE` | Plan reaches `BASELINE_FROZEN` state |
| `COMPLETED` | Admin manually marks village as completed |

### Rendering rules

- **Completed steps**: filled indicator, solid connector
- **Current step**: highlighted indicator, label in primary color, sub-status text below
- **Upcoming steps**: muted indicator, dashed connector
- Tracker is **display only** — not interactive in any view

### Sub-status label (beneath current step only)

| Current stage | Example sub-status |
|---|---|
| PROPOSAL | "Submitted — awaiting review" / "Amendment requested" / "Under review" |
| PLAN | "Plan submitted — under review" / "Baseline frozen, WIP active" |
| ACTIVE | "Year 1 of 3" / "Year 2 of 3" / "Year 3 of 3" |
| COMPLETED | "Programme completed" |

### JS component signature

```js
// components/VillageStageTracker.jsx
export function VillageStageTracker(container, { stage, subStatus }) {
  // renders stepper HTML into container element
}
```

`stage` and `sub_status` are always computed server-side and sent in every village API response — the frontend never derives them.

---

## Admin view — four tabs

### 1. Onboard
- Admin creates a village record (name, district, taluka, population)
- System generates a village login (username + temp password)
- Village user can now log in and create their proposal
- Admin can deactivate a village account

### 2. Manage Proposal
- Lists all proposals with status badges
- Selecting a village shows **VillageStageTracker** at top, then proposal detail
- Admin can: **review**, **edit**, **accept**, **request amendments**
- Village responds to amendment requests with a revised proposal
- Cycle: `SUBMITTED → UNDER_REVIEW → AMENDMENT_REQUESTED → AMENDED → ACCEPTED | DECLINED`
- Once accepted, village's Project tab activates

### 3. Manage Plan
- Lists submitted project plans per village
- Selecting a village shows **VillageStageTracker** at top, then plan detail
- Admin can: **review**, **edit**, **accept**
- On acceptance: baseline plan is **frozen** (read-only snapshot)
- System auto-creates a **WIP copy** from the baseline
- Admin can review the WIP plan as it evolves

### 4. Status
- Lists all status updates submitted by villages
- Selecting a village shows **VillageStageTracker** at top, then updates
- Admin can **mark** individual updates for donor visibility (`PUBLISHED`)
- Two communication channels per village:
  - **Update thread**: Q&A on a specific status post
  - **Village channel**: general ongoing message thread with village

---

## Village view — three tabs

**VillageStageTracker** is pinned at the top, visible across all tabs.

### 1. Proposal
- Village creates **one proposal only**
- Fields: focus area, description, community context, key activities planned
- If admin requests amendment: village edits and resubmits — repeatable
- Once accepted: tab becomes read-only, Project tab activates

### 2. Project *(locked until proposal accepted)*
- Village submits a 3-year plan with milestones per year
- Once admin accepts:
  - **Baseline** frozen (view only)
  - **WIP copy** created for tracking actuals
- Village sees baseline and WIP side by side

### 3. Status
- Free-form diary posts (not tied to milestones)
- Each post: text + multiple photos + multiple video clips
- Two communication surfaces:
  - **Post thread**: per-post Q&A with admin
  - **Village channel**: general thread with admin
- Village notified when admin publishes a post to donor view

---

## Donor view

- Only admin-published villages and updates are visible
- No admin/village communication visible
- **VillageStageTracker** shown (read-only)
- Access via shareable token-link or optional donor login

---

## Data model

### Internal status (drives stage + sub_status on backend)

```
CREATED → PROPOSAL_SUBMITTED → UNDER_REVIEW → AMENDMENT_REQUESTED
       → AMENDED → ACCEPTED | DECLINED
(after ACCEPTED) → PLAN_SUBMITTED → PLAN_REVIEW → PLAN_ACCEPTED
               → BASELINE_FROZEN → YEAR_1 → YEAR_2 → YEAR_3 → COMPLETED
```

### Stage derivation — `utils/stage.py`

```python
def derive_stage_and_substatus(internal_status: str) -> tuple[str, str]:
    PROPOSAL_STATES = {
        'CREATED': 'Not yet submitted',
        'PROPOSAL_SUBMITTED': 'Submitted — awaiting review',
        'UNDER_REVIEW': 'Under review',
        'AMENDMENT_REQUESTED': 'Amendment requested',
        'AMENDED': 'Amendment submitted — awaiting review',
    }
    PLAN_STATES = {
        'PLAN_SUBMITTED': 'Plan submitted — awaiting review',
        'PLAN_REVIEW': 'Plan under review',
        'PLAN_ACCEPTED': 'Plan accepted — WIP active',
        'BASELINE_FROZEN': 'Baseline frozen, WIP active',
    }
    ACTIVE_STATES = {
        'YEAR_1': 'Year 1 of 3',
        'YEAR_2': 'Year 2 of 3',
        'YEAR_3': 'Year 3 of 3',
    }
    if internal_status in PROPOSAL_STATES:
        return 'PROPOSAL', PROPOSAL_STATES[internal_status]
    if internal_status in PLAN_STATES:
        return 'PLAN', PLAN_STATES[internal_status]
    if internal_status in ACTIVE_STATES:
        return 'ACTIVE', ACTIVE_STATES[internal_status]
    return 'COMPLETED', 'Programme completed'
```

### Core tables

```sql
-- villages
id, name, district, taluka, population, state,
login_username, login_password_hash, is_active, bhau_enabled,
internal_status, created_at

-- proposals
id, village_id, status, focus_area, description, community_context,
submitted_at, reviewed_at, reviewer_notes
-- status: DRAFT | SUBMITTED | UNDER_REVIEW | AMENDMENT_REQUESTED | AMENDED | ACCEPTED | DECLINED

-- proposal_amendments
id, proposal_id, version_number, content, submitted_at, reviewed_at, reviewer_notes

-- project_plans
id, village_id, version_type, start_date, end_date, status, frozen_at, created_from_plan_id
-- version_type: BASELINE | WIP
-- status: DRAFT | SUBMITTED | UNDER_REVIEW | ACCEPTED | FROZEN

-- milestones
id, plan_id, year, title, description, is_completed, completed_at, notes

-- status_updates
id, village_id, description, submitted_at, is_published

-- media_files
id, status_update_id, media_type, file_url, caption, uploaded_at
-- media_type: PHOTO | VIDEO

-- update_threads
id, status_update_id, author_role, message, sent_at
-- author_role: ADMIN | VILLAGE

-- village_channels
id, village_id, author_role, message, sent_at, read_at
```

---

## Village API response shape

Every village record includes computed `stage` and `sub_status`:

```json
{
  "id": "...",
  "name": "Kusumbi",
  "district": "Sangli",
  "stage": "PROPOSAL",
  "sub_status": "Amendment requested",
  "internal_status": "AMENDMENT_REQUESTED",
  "is_active": true,
  "bhau_enabled": false
}
```

---

## API structure

```
-- Auth
POST   /auth/login
POST   /auth/logout

-- Admin: onboard
POST   /admin/villages
PATCH  /admin/villages/{id}/deactivate

-- Admin: proposals
GET    /admin/proposals
GET    /admin/proposals/{id}
PATCH  /admin/proposals/{id}/review
PATCH  /admin/proposals/{id}/accept
PATCH  /admin/proposals/{id}/request-amendment

-- Admin: plans
GET    /admin/plans
GET    /admin/plans/{id}
PATCH  /admin/plans/{id}/accept          # freezes baseline, creates WIP
GET    /admin/plans/{id}/wip

-- Admin: status
GET    /admin/status-updates
PATCH  /admin/status-updates/{id}/publish
PATCH  /admin/status-updates/{id}/unpublish

-- Shared: threads and channels
POST   /threads/{update_id}/messages
GET    /threads/{update_id}/messages
POST   /channels/{village_id}/messages
GET    /channels/{village_id}/messages

-- Village
GET    /village/me                       # includes stage + sub_status
POST   /village/proposal
PATCH  /village/proposal
GET    /village/proposal

POST   /village/plan
GET    /village/plan/baseline
GET    /village/plan/wip
PATCH  /village/plan/wip/milestones/{id}

POST   /village/status
GET    /village/status
POST   /village/status/{id}/media

-- Donor
GET    /donor/villages
GET    /donor/villages/{id}/updates
GET    /donor/villages/{id}/updates/{uid}/media
```

---

## Repository structure

```
pancham/
├── frontend/
│   ├── src/
│   │   ├── views/
│   │   │   ├── AdminView.jsx       # Admin tab shell: Onboard, Proposal, Plan, Status
│   │   │   ├── VillageView.jsx     # Village tab shell: Proposal, Project, Status
│   │   │   └── DonorView.jsx       # Donor feed
│   │   ├── components/
│   │   │   ├── VillageStageTracker.jsx   # shared — used in all three views
│   │   │   ├── Thread.jsx                # update-level Q&A
│   │   │   ├── VillageChannel.jsx        # general message channel
│   │   │   ├── MediaUploader.jsx         # photo + video upload
│   │   │   └── PlanViewer.jsx            # baseline vs WIP side-by-side
│   │   ├── api/
│   │   │   ├── client.js           # fetch wrapper, auth headers, error handling
│   │   │   ├── admin.js
│   │   │   ├── village.js
│   │   │   └── donor.js
│   │   ├── offline/
│   │   │   └── queue.js            # IndexedDB queue for offline status posts
│   │   ├── auth.js                 # JWT storage, login/logout
│   │   ├── router.js               # hash-based or history router
│   │   └── main.jsx
│   ├── sw.js                       # Service worker
│   ├── public/
│   │   └── manifest.json
│   └── vite.config.js
├── backend/
│   ├── main.py
│   ├── routers/
│   │   ├── auth.py
│   │   ├── admin_onboard.py
│   │   ├── admin_proposals.py
│   │   ├── admin_plans.py
│   │   ├── admin_status.py
│   │   ├── village_proposal.py
│   │   ├── village_plan.py
│   │   ├── village_status.py
│   │   ├── threads.py
│   │   ├── channels.py
│   │   ├── donor.py
│   │   └── bhau_bridge.py
│   ├── models/
│   │   ├── village.py
│   │   ├── proposal.py
│   │   ├── plan.py
│   │   ├── milestone.py
│   │   ├── status_update.py
│   │   ├── media.py
│   │   ├── thread.py
│   │   └── channel.py
│   ├── schemas/                    # Pydantic schemas per model
│   ├── utils/
│   │   └── stage.py                # derive_stage_and_substatus()
│   ├── db.py                       # async SQLAlchemy engine + session
│   ├── config.py                   # pydantic-settings, env vars
│   └── alembic/
│       └── versions/
├── CLAUDE.md
├── .env.example
└── railway.toml
```

---

## Key business rules

- One proposal per village at any time
- Amendment cycle repeatable; each requires admin acceptance to proceed
- Project tab locked until proposal is `ACCEPTED`
- Baseline plan immutable after freeze; WIP is the only editable copy
- `stage` and `sub_status` computed server-side in `utils/stage.py` — frontend never derives them
- Status post never shown to donor unless admin explicitly publishes it
- Donor sees zero data until admin has published at least one update per village
- Village channel and update threads are internal only — never donor-visible
- Bhau toggled per village via `village.bhau_enabled`

---

## Environment variables

```env
DATABASE_URL=postgresql+asyncpg://...
JWT_SECRET=...
JWT_ALGORITHM=HS256
STORAGE_BUCKET=pancham-media
STORAGE_URL=https://...
BHAU_API_URL=https://bhau.railway.app
BHAU_ENABLED=false
VITE_API_URL=https://pancham-server.up.railway.app
VITE_BHAU_ENABLED=false
```

---

## Dev setup

```bash
# Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install fastapi uvicorn "sqlalchemy[asyncio]" asyncpg alembic \
            pydantic pydantic-settings python-jose python-multipart
alembic upgrade head
uvicorn main:app --reload --port 8001

# Frontend
cd frontend
npm install
npm run dev
```

---

## Bhau integration

When `village.bhau_enabled` is true, a Bhau training panel appears in the Village Status tab. Proxies to Bhau FastAPI, responds in Marathi. Domains: FPO registration, mandi prices, SHG rules, government schemes, project plan guidance.

```python
# POST /bhau/ask
{ "question": "...", "lang": "mr", "village_id": "..." }
```

---

*Pancham — पंचम — development that resonates.*
