# Backend — Activity-Based Performance Tracker

## Phase status

- **Phase 1–4:** Models, admin, KPI services
- **Phase 5:** JWT auth + REST API under `/api/`

## Run (Windows 11)

```powershell
cd C:\Users\EF\Desktop\AUS\backend
.\venv\Scripts\activate
python manage.py migrate
python manage.py seed_default_kpi_weights
python manage.py runserver 8001
```

## Tests

```powershell
python manage.py test accounts.tests performance.tests
```

## API base

`http://127.0.0.1:8001/api/`

Auth login uses **email** + password. Send `Authorization: Bearer <access>`.
