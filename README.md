<div align="center">

# Industrial Wearable AI

**Real-time worker activity & risk monitoring for textile manufacturing**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Node](https://img.shields.io/badge/Node.js-18+-339933?logo=node.js&logoColor=white)](https://nodejs.org/)
[![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black)](https://react.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![ESP32](https://img.shields.io/badge/ESP32-PlatformIO-E7352C?logo=espressif&logoColor=white)](https://www.espressif.com/)

*Low-cost wearable (ESP32 + IMU) → Edge ML → Backend → Supervisor dashboard*

</div>

---

## Table of Contents

- [Overview](#overview)
- [Demo](#demo)
- [Features](#features)
- [System Architecture](#system-architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Documentation](#documentation)
- [Research](#research)
- [License](#license)

---

## Overview

**Industrial Wearable AI** is an end-to-end, human-centric system for **real-time monitoring of worker activity and risk** in textile manufacturing. It targets small and medium enterprises (SMEs) that need visibility into who is working, idle, or at risk—without the cost of full Industry 4.0 platforms.

| Layer | Role |
|-------|------|
| **Wearable** | ESP32 + IMU (MPU6050/MPU9250) streams raw motion over BLE |
| **Edge** | Python on laptop: BLE client, feature extraction, ML/rule-based classifier → activity + risk |
| **Backend** | FastAPI + PostgreSQL: stores events, broadcasts live state over WebSocket |
| **Dashboard** | React: login, live workers, alerts, KPIs, charts, shift summary |

**Deployment:** All non-wearable components run on a **single laptop** (no Raspberry Pi or cloud required). Optional Docker for PostgreSQL.

---

## Demo

<!-- INSERT IMAGE 1: Hero / system overview or dashboard home -->
<!-- Suggested: Screenshot of dashboard Live Overview, or a collage: wearable + laptop + dashboard -->
<!-- Save as: docs/images/readme-hero.png (recommended size: 1200×600 or 16:9) -->

<p align="center">
  <img src="docs/images/readme-hero.png" alt="Industrial Wearable AI — System overview or dashboard" width="800"/>
</p>
<p align="center"><sub><i>Add your image: system overview or dashboard home (e.g. docs/images/readme-hero.png)</i></sub></p>

<!-- INSERT IMAGE 2: Supervisor dashboard — Live Overview with workers, KPIs, alerts -->
<!-- Suggested: Full-screen or cropped screenshot of Live Overview: worker cards, KPIs, alerts panel, charts -->
<!-- Save as: docs/images/readme-dashboard.png -->

<p align="center">
  <img src="docs/images/readme-dashboard.png" alt="Supervisor dashboard — Live Overview" width="800"/>
</p>
<p align="center"><sub><i>Add your image: supervisor dashboard Live Overview (e.g. docs/images/readme-dashboard.png)</i></sub></p>

<!-- INSERT IMAGE 3 (optional): Wearable device / hardware -->
<!-- Suggested: Photo of ESP32 board with MPU6050 on wrist or desk -->
<!-- Save as: docs/images/readme-wearable.png -->

<p align="center">
  <img src="docs/images/readme-wearable.png" alt="Wearable device — ESP32 + IMU" width="500"/>
</p>
<p align="center"><sub><i>Add your image: wearable hardware (e.g. docs/images/readme-wearable.png)</i></sub></p>

---

## Features

- **Real-time activity recognition** — Sewing, idle, adjusting, break, error from wrist IMU
- **Risk flags** — Ergonomic and fatigue risk (rule-based or from model)
- **Live supervisor dashboard** — Worker cards, KPIs (Live / Working / Idle / At risk), alerts panel, state donut, activity timeline
- **Historical views** — Session history, activity timeline (1 h / 6 h / 24 h), shift summary
- **WebSocket updates** — Live state and sensor data without refresh
- **No-IMU handling** — Clear “No MPU connected” when sensor is absent or faulty
- **Demo mode** — Edge simulator and seed data for testing without hardware
- **Single-laptop deployment** — Backend, edge, and dashboard on one machine; PostgreSQL via Docker or local

---

## System Architecture

<!-- INSERT IMAGE 4: High-level architecture diagram -->
<!-- Suggested: Export from docs/uml/00-context.puml or 02-component.puml (PlantUML) as PNG/SVG -->
<!-- Save as: docs/images/readme-architecture.png -->

<p align="center">
  <img src="docs/images/readme-architecture.png" alt="System architecture — Wearable, Edge, Backend, Dashboard" width="700"/>
</p>
<p align="center"><sub><i>Add your image: architecture diagram from docs/uml/ (e.g. docs/images/readme-architecture.png)</i></sub></p>

**Flow in short:**

```
Wearable (ESP32 + IMU) --BLE--> Edge (Python: buffer → features → classifier)
                                    |
                                    +-- HTTP POST /events, /live/sensor
                                    v
Backend (FastAPI + PostgreSQL) ---- WebSocket ----► Dashboard (React)
```

More diagrams (use case, component, deployment, sequence, class, activity, state) are in **`docs/uml/`** (PlantUML). Export and add to `docs/images/` if you want them in the repo or in the research paper.

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| **Wearable** | ESP32 (PlatformIO/Arduino), MPU6050/MPU9250, NimBLE, ArduinoJson |
| **Edge** | Python 3.10+, bleak (BLE), scikit-learn/joblib, aiohttp, numpy, pandas |
| **Backend** | FastAPI, SQLAlchemy (async), PostgreSQL (asyncpg), Alembic, JWT, WebSocket |
| **Dashboard** | React 19, TypeScript, Vite, Recharts, Framer Motion, Zustand, Axios |
| **ML** | scikit-learn, joblib (saved model); optional training in `ml/` |

| Service | URL (default) |
|---------|----------------|
| Backend API | http://localhost:8000 |
| API docs | http://localhost:8000/docs |
| WebSocket | ws://localhost:8000/ws/live |
| Dashboard | http://localhost:5173 |

---

## Project Structure

```
Industrial_Wearable_AI/
├── backend/          # FastAPI, PostgreSQL, WebSocket, JWT, Alembic
├── dashboard/        # React (Vite) supervisor UI
├── edge/             # BLE client, ML pipeline, API client (Python)
├── firmware/        # ESP32 (PlatformIO) — wearable firmware
├── ml/               # Training scripts, simulator, data (optional)
├── scripts/          # Utility scripts
└── docs/             # Documentation, UML, research paper, run guides
    ├── uml/          # PlantUML diagrams (context, use case, component, deployment, sequence, class, activity, state)
    └── images/       # Add README/diagram images here (readme-hero.png, readme-dashboard.png, etc.)
```

---

## Prerequisites

- **Python 3.10+** (backend, edge, optional ML)
- **Node.js 18+** (dashboard)
- **PostgreSQL** — via [Docker](https://www.docker.com/) (recommended) or local install
- **Git**

Optional for hardware:

- **PlatformIO** (VS Code extension or CLI) for building/flashing firmware
- **BLE** on laptop or USB BLE dongle for connecting to the wearable

---

## Installation

### 1. Clone the repository

```powershell
git clone https://github.com/YOUR_USERNAME/Industrial_Wearable_AI.git
cd Industrial_Wearable_AI
```

*(Replace `YOUR_USERNAME` with your GitHub username.)*

### 2. Backend (FastAPI + PostgreSQL)

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1   # Windows PowerShell
# source .venv/bin/activate   # Linux/macOS
pip install -r requirements.txt
```

Create `backend/.env` (copy from `.env.example` if present) with at least:

- `DB_URL=postgresql+asyncpg://user:password@localhost:5432/industrial_wearable`
- `JWT_SECRET=<your-secret>`

Start PostgreSQL (Docker):

```powershell
docker compose up -d
```

Apply migrations and seed admin user (and optional demo workers):

```powershell
alembic upgrade head
python seed_user.py
python seed_demo_workers.py   # optional: W01–W08 with 45 days history
```

### 3. Edge (Python)

```powershell
cd edge
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create `edge/.env` if needed (e.g. `BACKEND_URL=http://localhost:8000`, `BLE_DEVICE_ID=` for simulator).

### 4. Dashboard (React)

```powershell
cd dashboard
npm install
```

Create `dashboard/.env` if needed (e.g. `VITE_API_BASE_URL=http://localhost:8000`).

### 5. Firmware (optional — when hardware is ready)

```powershell
cd firmware
pio run              # Build
pio run -t upload    # Flash to ESP32
```

See **`firmware/README.md`** and **`docs/HARDWARE_CONNECTIONS.md`** for wiring and config.

---

## Quick Start

Run services in order (use separate terminals for backend, edge, dashboard):

```powershell
# Terminal 1 — PostgreSQL (if not already up)
cd backend && docker compose up -d

# Terminal 2 — Backend
cd backend && .venv\Scripts\Activate.ps1
uvicorn app.main:app --reload

# Terminal 3 — Edge (simulator mode if BLE_DEVICE_ID is empty)
cd edge && .venv\Scripts\Activate.ps1 && python -m src.main

# Terminal 4 — Dashboard
cd dashboard && npm run dev
```

Then:

1. Open **http://localhost:5173**
2. Login: **`admin`** / **`admin123`**
3. Use **Live Overview** for real-time workers, alerts, and charts; **Shift Summary** for sessions.

**Before any pilot:** Change the default password and set production env vars — see **`docs/PILOT_PREP.md`**.

```powershell
cd backend && python change_password.py admin
```

---

## Configuration

| Location | Purpose |
|----------|---------|
| `backend/.env` | `DB_URL`, `JWT_SECRET`, CORS, etc. |
| `edge/.env` | `BACKEND_URL`, `BLE_DEVICE_ID` (empty = simulator) |
| `dashboard/.env` | `VITE_API_BASE_URL` |
| `firmware/` | `WORKER_ID`, `MPU_I2C_ADDR`, BLE UUIDs (in code or platformio.ini) |

Details: **`docs/PROJECT_DOCUMENTATION.md`** (Configuration section) and **`docs/TECHNICAL_STACK_SPEC.md`**.

---

## Documentation

| Document | Description |
|----------|-------------|
| **docs/PROJECT_DOCUMENTATION.md** | Full project docs: architecture, features, APIs, run, troubleshooting |
| **docs/RUN_ORDER.md** | Step-by-step service startup and shutdown |
| **docs/RUN_COMMANDS.md** | Commands for Docker and PostgreSQL on Windows |
| **docs/HARDWARE_CONNECTIONS.md** | Wiring (MPU6050/MPU9250, temp), troubleshooting |
| **docs/TECHNICAL_STACK_CLARIFIED.md** | Stack choices and rationale |
| **docs/TESTING_WITHOUT_HARDWARE.md** | Test with edge simulator and seed data |
| **docs/PILOT_PREP.md** | Pilot deployment checklist (password, env) |
| **docs/uml/README.md** | PlantUML diagrams: how to generate and map to research paper |

---

## Research

A full **research paper** (problem, related work, architecture, implementation, evaluation, references) is in **`docs/RESEARCH_PAPER.md`**. It includes placeholders for figures and tables; diagram sources are in **`docs/uml/`**. You can export PlantUML to PNG/SVG and add to **`docs/figures/`** or **`docs/images/`** as needed.

---

## License

*(Add your license here, e.g. MIT, Apache 2.0, or "All rights reserved.")*

---

<div align="center">

**Industrial Wearable AI** — Real-time worker activity & risk monitoring for textile manufacturing.

</div>
