# Activity-Based Performance Tracker

A secure Activity-Based Performance and KPI Tracking System for recording assigned and completed work, supervisor verification, and contribution metrics for interns, trainees, junior officers, and staff.

**Important:** Scores in this application are an **Activity Performance Score** / **Contribution Score**. They are **not** an official government performance appraisal.

---

## Features (planned)

- Role-based access: Intern/Staff, Supervisor, Administrator
- Task assignment, draft → submit → approve/reject workflow
- Evidence uploads and supervisor quality ratings
- Configurable KPI weights and Contribution Score calculations
- Dashboards, weekly/monthly reports, and CSV export
- JWT authentication and audit logging

> Phases 1–5: backend complete. Phase 6: React auth, dashboards, and role-based pages.

---

## Technology stack

| Layer | Stack |
|-------|--------|
| Frontend | React (Vite), JavaScript, React Router, Axios, Recharts, React Toastify, Bootstrap |
| Backend | Python, Django, Django REST Framework, SimpleJWT, django-cors-headers |
| Database | PostgreSQL |

---

## Folder structure (Phase 2)

```
AUS/
├── .gitignore
├── README.md
├── backend/
│   ├── manage.py
│   ├── config/           # Django project settings (AUTH_USER_MODEL set)
│   ├── accounts/         # Custom User model + admin
│   ├── departments/      # Department model + admin
│   ├── tasks/            # TaskCategory model + admin (Task model in Phase 3)
│   ├── attendance/
│   ├── performance/
│   ├── reports/
│   ├── audit/
│   ├── media/
│   ├── requirements.txt
│   ├── .env.example
│   └── README.md
└── frontend/
    ├── public/
    ├── src/
    │   ├── api/
    │   ├── components/
    │   ├── context/
    │   ├── hooks/
    │   ├── pages/
    │   ├── routes/
    │   ├── services/
    │   ├── utils/
    │   ├── App.jsx
    │   └── main.jsx
    ├── .env.example
    ├── package.json
    └── README.md
```
---

## Prerequisites (Windows 11)

Install and verify:

| Software | Verify command |
|----------|----------------|
| Python 3.11+ | `python --version` |
| Node.js 20 LTS+ and npm | `node -v` then `npm -v` |
| PostgreSQL 15+ and pgAdmin 4 | Service running in Windows Services |
| Git | `git --version` |

---

## PostgreSQL setup (pgAdmin)

1. Open **pgAdmin 4** and connect to your local PostgreSQL server.
2. Right-click **Databases** → **Create** → **Database**.
3. Set **Database** name to `kpi_tracker`.
4. Set **Owner** to your PostgreSQL role (often `postgres`).
5. Click **Save**.

Remember the password for your PostgreSQL user; you will put it in `backend/.env` as `DB_PASSWORD`.

---

## Environment variables

### Backend

1. Copy the example file:

```powershell
cd C:\Users\EF\Desktop\AUS\backend
copy .env.example .env
```

2. Edit `backend\.env` and set at least:

- `SECRET_KEY` — a long random string (do not commit this file)
- `DB_PASSWORD` — your PostgreSQL password
- Confirm `DB_NAME=kpi_tracker`, `DB_USER`, `DB_HOST`, `DB_PORT`

### Frontend

```powershell
cd C:\Users\EF\Desktop\AUS\frontend
copy .env.example .env
```

Default:

```
VITE_API_BASE_URL=http://127.0.0.1:8000/api
```

---

## Backend setup (Windows 11)

```powershell
cd C:\Users\EF\Desktop\AUS\backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

Apply Django built-in migrations (Phase 1 — no custom models yet):

```powershell
python manage.py migrate
```

Optional (later phases will use role-based admin users):

```powershell
python manage.py createsuperuser
```

Start the development server:

```powershell
python manage.py runserver
```

If port **8000** is already in use (for example by Splunk), use another port:

```powershell
python manage.py runserver 8001
```

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) (or `:8001`) — you should see a JSON health response.

Admin (after migrate + createsuperuser): [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/) (or `:8001/admin/`).

Createsuperuser uses **email** (not username):

```powershell
python manage.py createsuperuser
```

You will be prompted for email, first name, last name, employee/intern number, and password.
---

## Frontend setup (Windows 11)

```powershell
cd C:\Users\EF\Desktop\AUS\frontend
npm install
npm run dev
```

Open the URL Vite prints (usually [http://localhost:5173/](http://localhost:5173/)).

---

## Git

The repository root is `AUS/`. `.env` files are ignored by `.gitignore` — never commit secrets or database passwords.

```powershell
cd C:\Users\EF\Desktop\AUS
git status
```

---

## Running tests

Not applicable in Phase 1. Backend and frontend tests will be added in a later phase.

```powershell
# Backend (later)
cd C:\Users\EF\Desktop\AUS\backend
.\venv\Scripts\activate
python manage.py test

# Frontend (later)
cd C:\Users\EF\Desktop\AUS\frontend
npm test
```

---

## Phase 1 verification checklist

Confirm each item before requesting Phase 2:

1. **PostgreSQL is running** — Windows Services shows the PostgreSQL service as Running; pgAdmin connects; database `kpi_tracker` exists.
2. **Virtual environment activates** — After `.\venv\Scripts\activate`, the prompt shows `(venv)` and `where python` points under `backend\venv`.
3. **Django starts** — `python manage.py runserver` works; [http://127.0.0.1:8000/](http://127.0.0.1:8000/) returns JSON with `"status": "ok"`.
4. **React Vite starts** — `npm run dev` works; [http://localhost:5173/](http://localhost:5173/) shows the default Vite React page.
5. **Folders are correct** — `backend\` has `config\` plus apps `accounts`, `departments`, `tasks`, `attendance`, `performance`, `reports`, `audit`, and `media\`; `frontend\src\` has `api`, `components`, `context`, `hooks`, `pages`, `routes`, `services`, `utils`.
6. **Git is initialized** — `git status` works at `AUS\`; `.env` files do not appear as files to commit (they are ignored).
7. **Environment files** — `backend\.env.example` and `frontend\.env.example` exist; local `.env` copies exist with your `SECRET_KEY` and `DB_PASSWORD` filled in.

If `python manage.py migrate` fails with a password or connection error, fix `DB_PASSWORD` / host / port in `backend\.env` and ensure the `kpi_tracker` database exists in pgAdmin.

---

## Phase 2 — Models

Phase 2 adds:

- **Department** (`departments.Department`)
- **Custom User** (`accounts.User`) with roles `INTERN`, `STAFF`, `SUPERVISOR`, `ADMIN`, email login, department, and supervisor
- **TaskCategory** (`tasks.TaskCategory`) with difficulty levels and default expected output/duration
- Django admin registration for all three
- `AUTH_USER_MODEL = 'accounts.User'`

**Note:** Switching to a custom user model required recreating the empty `kpi_tracker` database and re-running migrations. Do not change `AUTH_USER_MODEL` again after you have real data.

### Phase 2 verification checklist

1. Migrations applied — `python manage.py showmigrations accounts departments tasks` shows `[X]` for `0001_initial`.
2. `AUTH_USER_MODEL` is `accounts.User` — confirmed in settings / Django shell.
3. Create a department in admin or shell.
4. Create a task category in admin or shell.
5. Create a superuser — `python manage.py createsuperuser` (email-based).
6. Log into admin — Users, Departments, and Task categories are listed.
7. Health endpoint returns `"phase": 2`.
8. Restart `runserver` after pulling Phase 2 (use port `8001` if 8000 is taken).

---

## Phase 3 — Task and evidence models

Phase 3 adds:

- **Task** (`tasks.Task`) with assignment, schedule, output, difficulty, workflow status, supervisor ratings, and review timestamps
- **TaskEvidence** (`tasks.TaskEvidence`) with file upload under `media/task_evidence/`
- Statuses: `DRAFT`, `PENDING`, `APPROVED`, `REJECTED`, `COMPLETED`, `CANCELLED`
- Model validation: due date vs assigned date, end time after start time, non-negative outputs, ratings 1–5
- Auto-fill of expected output/duration from category defaults when missing
- Auto-calculate `actual_duration_minutes` from start/end time when possible
- Admin screens with evidence inline; media serving in `DEBUG`
- Upload size / allowed extension settings prepared for API validation later

Only **APPROVED** tasks are intended to contribute to Contribution Score calculations (KPI services come next).

### Phase 3 verification checklist

1. Run `python manage.py migrate` — `tasks.0002_...` is applied.
2. Restart `python manage.py runserver 8001`.
3. Health endpoint returns `"phase": 3`.
4. In admin, create a Department, User (or use superuser), and Task category if needed.
5. Create a **Task** in draft status with title, category, and assigned user.
6. Confirm expected output/duration fill from the category when left blank.
7. Attach **Task evidence** (inline on the task or via Task evidence admin).
8. Confirm Tasks and Task evidence appear in the admin index.

---

## Phase 4 — Attendance, KPI models, and calculation services

Phase 4 adds:

- **AttendanceRecord** — PRESENT / ABSENT / LATE / OFFICIAL_DUTY / LEAVE
- **KPIWeight** — configurable weights; active weights must total 100%
- **PerformanceSnapshot** — stored weekly/monthly/quarterly Contribution Scores
- **AuditLog** — action trail (read-only in admin except superuser delete)
- **KPI services** in [`performance/services.py`](backend/performance/services.py): completion, output, time efficiency, quality, accuracy, timeliness, attendance, overall score (capped at 100), classifications
- Management command: `python manage.py seed_default_kpi_weights`
- Formula unit tests: `python manage.py test performance.tests`

Default weights: Completion 25%, Output 25%, Time 15%, Quality 20%, Accuracy 10%, Attendance 5%.

### Phase 4 verification checklist

1. `python manage.py migrate` — attendance, performance, audit `0001_initial` applied.
2. `python manage.py seed_default_kpi_weights` — reports total `100.00%`.
3. Restart `runserver 8001`; health endpoint shows `"phase": 4`.
4. Admin shows Attendance records, KPI weights, Performance snapshots, Audit logs.
5. `python manage.py test performance.tests` — all pass.
6. (Optional) Add an attendance row for your user; leave KPI weight editing to the seed defaults unless you rebalance all active weights to 100%.

---

## Phase 5 — JWT auth and REST API

Phase 5 wires the backend API under `/api/` with role-based permissions.

### Auth

| Method | Endpoint | Notes |
|--------|----------|--------|
| POST | `/api/auth/register/` | INTERN/STAFF self-registration |
| POST | `/api/auth/login/` | Returns `access`, `refresh`, `user` (email + password) |
| POST | `/api/auth/token/refresh/` | Refresh access token |
| GET | `/api/auth/me/` | Current user profile |
| POST | `/api/auth/change-password/` | Requires old + new password |

### Resources

| Area | Endpoints |
|------|-----------|
| Users | `/api/users/`, `/api/users/{id}/`, `/api/users/my-team/` |
| Departments | `/api/departments/` |
| Categories | `/api/task-categories/` |
| Tasks | `/api/tasks/`, `my-tasks/`, `pending-review/`, `{id}/submit/`, `approve/`, `reject/`, `evidence/` |
| Attendance | `/api/attendance/` |
| KPI weights | `/api/kpi-weights/` |
| Dashboard | `/api/dashboard/summary/`, `weekly/`, `monthly/`, `team-summary/` |
| Reports | `/api/reports/user/{id}/`, `weekly/`, `monthly/`, `category-breakdown/`, `status-breakdown/`, `export/csv/` |

Login example (PowerShell):

```powershell
Invoke-RestMethod -Method POST -Uri http://127.0.0.1:8001/api/auth/login/ -ContentType "application/json" -Body '{"email":"your@email.com","password":"your-password"}'
```

Use header: `Authorization: Bearer <access_token>`

### Phase 5 verification checklist

1. Restart `python manage.py runserver 8001`
2. Health endpoint returns `"phase": 5`
3. Login via `/api/auth/login/` returns tokens
4. `GET /api/auth/me/` with Bearer token returns your profile
5. Create → submit → approve a task (approver must not be the assignee)
6. `python manage.py test accounts.tests performance.tests` passes
7. Frontend `.env` has `VITE_API_BASE_URL=http://127.0.0.1:8001/api`

---

## Security notes

- Do not commit `.env`, secrets, or real employee data.
- Scores are Contribution / Activity Performance Scores only — not official appraisals.
- API uses JWT Bearer tokens. Development may store tokens in localStorage; **HTTP-only secure cookies are recommended for production**.
- Never trust frontend role checks alone — permissions are enforced on the backend.
- Users cannot approve or reject their own tasks.

---

## Phase 6 — React frontend

Phase 6 connects the Vite React app to the API.

- JWT login with axios interceptors (access + refresh); tokens in localStorage for development (prefer HTTP-only cookies in production)
- `AuthContext`, protected routes, and role guards
- Responsive sidebar layout with Contribution Score disclaimer
- Personal, supervisor, and admin dashboards (Recharts + metric cards)
- Task create/edit/detail, submit, evidence upload, supervisor review (approve/reject)
- Attendance, profile, reports/CSV export, user/department/category/KPI admin screens
- Toast notifications, loading/empty/error states, confirmation dialog

### Phase 6 verification checklist

1. Backend: `python manage.py runserver 8001`
2. Frontend: `cd frontend` → `npm run dev` → http://localhost:5173/
3. Sign in with an existing user (admin or intern)
4. Confirm role-based home: ADMIN → `/admin`, SUPERVISOR → `/supervisor`, INTERN/STAFF → `/dashboard`
5. Create a draft task, submit it, approve as a different supervisor user
6. Open Performance report and confirm Overall Activity Score label/disclaimer

---

## Future improvements

- Full fictional seed data command
- Broader automated tests, PDF export, polish charts
- Production cookie-based JWT storage

---

## License

Development project — configure licensing as required by your organization.
