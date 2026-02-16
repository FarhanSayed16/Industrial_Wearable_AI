# Industrial Wearable AI — Technical Stack (Clarified)

**Document:** Clear, consolidated technical stack with rationale.  
**Purpose:** Single source of truth for "what we're using and why."  
**Version:** 1.0  
**Last updated:** 2025

---

## Table of Contents

1. [What We Are Building](#1-what-we-are-building)
2. [Recommended Stack (Best Specs)](#2-recommended-stack-best-specs)
3. [End-to-End Flow](#3-end-to-end-flow)
4. [Why Python for Backend & Edge?](#4-why-python-for-backend--edge)
5. [Best Specs Summary](#5-best-specs-summary)
6. [What We Are NOT Using (MVP)](#6-what-we-are-not-using-mvp)
7. [Optional Future Additions](#7-optional-future-additions)
8. [One-Line Stack Summary](#8-one-line-stack-summary)
9. [Deployment: Laptop-Only Setup](#9-deployment-laptop-only-setup)

---

## 1. What We Are Building

| Component | What It Is | Purpose |
|-----------|------------|---------|
| **Wearable device** | ESP32 + sensors on wrist | Captures motion + temperature; sends raw data via BLE |
| **Edge gateway** | Laptop (Python) | Receives BLE, runs ML, sends labels to backend |
| **Backend server** | Python API (FastAPI) | Stores data, aggregates, broadcasts live state |
| **Web dashboard** | React web app | Supervisor views live workers, alerts, shift summary |
| **Mobile app** | Not in MVP | Optional later (e.g. Flutter) |

**Summary:** Wearable + Edge + Backend + Web Dashboard. No mobile app in MVP.

---

## 2. Recommended Stack (Best Specs)

### 2.1 Wearable (Hardware + Firmware)

| Layer | Choice | Why |
|-------|--------|-----|
| **MCU** | **ESP32-WROOM-32** | BLE + WiFi built-in; cheap; well-documented |
| **IMU** | **MPU6050** | 6-axis motion (accel + gyro); low cost |
| **Temperature** | **DHT11** or **DS18B20** | Simple, cheap |
| **IDE** | **PlatformIO** (VS Code) or **Arduino IDE** | PlatformIO preferred for project structure |
| **Language** | **C++ (Arduino)** | Simple; good library support |
| **Connectivity** | **BLE 4.2** | Low power; ~10 m range |

**Why not Arduino Uno?** No BLE. ESP32 has BLE built-in.

**Why not ESP8266?** No BLE. ESP32 is the right choice.

---

### 2.2 Edge Gateway (Python)

| Layer | Choice | Why |
|-------|--------|-----|
| **Device** | **Laptop** | Runs Python + ML (no Raspberry Pi) |
| **Language** | **Python 3.10+** | ML ecosystem (scikit-learn, numpy, pandas) |
| **BLE** | **bleak** | Async BLE client |
| **ML** | **scikit-learn**, **joblib** | Activity classification |
| **HTTP** | **aiohttp** or **requests** | POST to backend |

---

### 2.3 Backend

| Layer | Choice | Why |
|-------|--------|-----|
| **Framework** | **FastAPI** (Python) | Async, WebSocket, OpenAPI, fast |
| **Server** | **Uvicorn** | ASGI server for FastAPI |
| **Database** | **PostgreSQL** | Relational, time-series friendly, robust |
| **ORM** | **SQLAlchemy 2.x** (async) | Mature, async support |
| **Auth** | **JWT** (PyJWT) | Stateless auth |

#### Why PostgreSQL, NOT MongoDB?

| Aspect | PostgreSQL | MongoDB |
|--------|------------|---------|
| **Data shape** | Workers, sessions, events, aggregates — relational | Same, but joins are awkward |
| **Queries** | JOINs, aggregates, time ranges — natural | Manual aggregation |
| **Consistency** | ACID | Eventual consistency |
| **Time-series** | Excellent with indexes | Possible but not ideal |
| **Fit for this project** | ✅ Strong | ❌ Weaker |

For workers, sessions, events, and aggregates — **PostgreSQL is the right choice**.

---

### 2.4 Web Dashboard

| Layer | Choice | Why |
|-------|--------|-----|
| **Framework** | **React 18** | Industry standard; huge ecosystem |
| **Build** | **Vite** | Fast dev server and build |
| **Language** | **TypeScript** | Type safety |
| **Charts** | **Recharts** or **Chart.js** | Charts for trends/summary |
| **UI** | **Tailwind** or **MUI** | Fast styling |
| **State** | **Zustand** or React Context | Simple state management |
| **Realtime** | **WebSocket** | Live updates |

#### Why React, NOT Flutter for Web?

- Flutter web is newer; less mature for dashboards.
- React has more libraries (charts, WebSocket, auth).
- Supervisor dashboard is primarily desktop — React fits.

**Flutter later:** For a native mobile app for supervisors (walking the floor), Flutter is a good option in Phase 2+.

---

## 3. End-to-End Flow

```
┌─────────────────┐     BLE      ┌──────────────────┐     HTTP/WS     ┌─────────────────┐
│  ESP32 Wearable │ ────────────► │  Edge (Python)   │ ──────────────► │  Backend        │
│  Arduino C++    │               │  Laptop         │                 │  FastAPI        │
│  MPU6050+DHT11  │               │  bleak + sklearn │                 │  PostgreSQL     │
└─────────────────┘               └──────────────────┘                 └────────┬────────┘
                                                                                  │
                                                                                  │ WebSocket
                                                                                  ▼
                                                                         ┌─────────────────┐
                                                                         │  React Dashboard │
                                                                         │  (Web Browser)   │
                                                                         └─────────────────┘
```

---

## 4. Why Python for Backend & Edge?

| Reason | Detail |
|--------|--------|
| **ML ecosystem** | scikit-learn, pandas, numpy, joblib — industry standard |
| **Single language** | Edge and backend both Python — less context switching |
| **FastAPI** | Async, WebSocket, auto docs — modern Python |
| **Cost** | Free, open-source |
| **Team skills** | Python is common in data/ML projects |

**Alternatives (Node.js, Go, etc.):** Would require a separate ML stack (Python for ML, another language for API) — more complexity.

---

## 5. Best Specs Summary

| Component | Technology |
|-----------|------------|
| **Wearable MCU** | ESP32-WROOM-32 |
| **Wearable IDE** | PlatformIO (VS Code) or Arduino IDE |
| **Wearable language** | C++ (Arduino) |
| **Edge** | Python 3.10+ on laptop |
| **Backend** | FastAPI + Uvicorn |
| **Database** | PostgreSQL 14/15 |
| **Dashboard** | React 18 + TypeScript + Vite |
| **Realtime** | WebSocket |

---

## 6. What We Are NOT Using (MVP)

| Not used | Reason |
|----------|--------|
| **MongoDB** | PostgreSQL fits relational + time-series better |
| **Flutter (web)** | React is better for this dashboard |
| **Node.js backend** | Python needed for ML; FastAPI is excellent |
| **Arduino Uno** | No BLE |
| **Cloud DB (Firebase)** | On-prem first; PostgreSQL is sufficient |

---

## 7. Optional Future Additions

| Addition | When |
|----------|------|
| **Flutter mobile app** | After web dashboard is stable |
| **Cloud backend (AWS/GCP)** | For multi-site deployment |
| **Redis** | If we need caching or pub/sub at scale |

---

## 8. One-Line Stack Summary

**ESP32 (Arduino C++) → BLE → Python Edge on Laptop (scikit-learn) → FastAPI + PostgreSQL → React Web Dashboard**

---

## 9. Deployment: Laptop-Only Setup

All components run on a single laptop:

| Component | Where It Runs |
|-----------|---------------|
| **Edge gateway** | Laptop (Python) |
| **Backend** | Laptop (FastAPI + Uvicorn) |
| **PostgreSQL** | Laptop (local or Docker) |
| **Dashboard** | Laptop (React dev server) or browser |

**Hardware needed:** Laptop + USB BLE dongle (if laptop has no BLE) + ESP32 wearable(s). No Raspberry Pi required.

---

## Related Documents

- `TECHNICAL_STACK_SPEC.md` — Full hardware/software specifications
- `IMPLEMENTATION_PLAN.md` — Step-by-step implementation guide
