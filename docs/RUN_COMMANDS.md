# Industrial Wearable AI — Commands to Run the Project

Run these in **order**, each in a **separate terminal** (PowerShell or Command Prompt).

---

## Prerequisites

- **PostgreSQL** — via Docker (see Terminal 1) **or** [install on Windows](#run-without-docker-postgres-on-windows) (use this if Docker gives 500 error)
- **Python 3.10+** — for backend and edge
- **Node.js 18+** — for dashboard

---

## Run without Docker (PostgreSQL on Windows)

If Docker keeps giving **"500 Internal Server Error"** when pulling the Postgres image, use a local PostgreSQL install instead.

### 1. Install PostgreSQL

1. Download the installer: **https://www.postgresql.org/download/windows/** (e.g. PostgreSQL 15 or 16).
2. Run the installer. During setup:
   - Set a password for the **postgres** user (e.g. `postgres`).
   - Keep port **5432**.
   - Install Stack Builder is optional (you can skip it).
3. After install, ensure the **PostgreSQL** service is running (Services → postgresql-x64-15).

### 2. Create the database

Open **pgAdmin** (installed with PostgreSQL) or **psql** and run:

```sql
CREATE DATABASE wearable_ai;
```

(If you use a different user/password, note them for the next step.)

### 3. Point the backend to local Postgres

In `D:\Industrial_Wearable_AI\backend`, create or edit **`.env`**:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/wearable_ai
```

Replace `postgres:postgres` with your PostgreSQL username and password if different.

### 4. Run the project (no Docker)

- **Skip Terminal 1** (no `docker compose`).
- Run **Terminal 2** (backend): migrations, seed, then `uvicorn app.main:app --reload`.
- Run **Terminal 3** (edge) and **Terminal 4** (dashboard) as below.

---

## Terminal 1: PostgreSQL (Docker)

```powershell
cd D:\Industrial_Wearable_AI\backend
docker compose up -d
```

Wait ~10 seconds for Postgres to be ready. Check: `docker compose ps`

**If you see "500 Internal Server Error" when pulling the image:**

Use **PostgreSQL on Windows** instead — see **[Run without Docker](#run-without-docker-postgres-on-windows)** above. No Docker needed.

If you prefer to fix Docker: try `docker pull postgres:14`, restart Docker Desktop, or update Docker Desktop to the latest version.

---

## Terminal 2: Backend

```powershell
cd D:\Industrial_Wearable_AI\backend
```

Create and activate a virtual environment (first time only):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Apply migrations and seed data (first time or after DB reset):

```powershell
alembic upgrade head
python seed_user.py
python seed_demo_workers.py
```

Start the backend:

```powershell
uvicorn app.main:app --reload
```

Backend: **http://localhost:8000** — API docs: **http://localhost:8000/docs**

---

## Terminal 3: Edge Gateway

```powershell
cd D:\Industrial_Wearable_AI\edge
```

Create and activate venv (first time only):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Start the edge (simulator mode if no BLE device):

```powershell
python -m src.main
```

To use a real ESP32, set in `edge\.env`: `BLE_DEVICE_ID=a4:f0:0f:8e:9c:1a` and `WORKER_ID=W01`.

---

## Terminal 4: Dashboard

```powershell
cd D:\Industrial_Wearable_AI\dashboard
npm install
npm run dev
```

Dashboard: **http://localhost:5173** (or the port Vite prints)

Login: **admin** / **admin123**

---

## Quick reference (after first-time setup)

| Terminal | Command |
|----------|---------|
| 1 | `cd D:\Industrial_Wearable_AI\backend` then `docker compose up -d` |
| 2 | `cd D:\Industrial_Wearable_AI\backend` then `.venv\Scripts\Activate.ps1` then `uvicorn app.main:app --reload` |
| 3 | `cd D:\Industrial_Wearable_AI\edge` then `.venv\Scripts\Activate.ps1` then `python -m src.main` |
| 4 | `cd D:\Industrial_Wearable_AI\dashboard` then `npm run dev` |

---

## Stop everything

1. In each terminal: **Ctrl+C**
2. Stop Postgres: `cd D:\Industrial_Wearable_AI\backend` then `docker compose down`
