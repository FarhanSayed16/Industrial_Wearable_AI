# Industrial Wearable AI — Laptop-Only Deployment

**Document:** Deployment setup using a single laptop. No Raspberry Pi.  
**Version:** 1.0  
**Last updated:** 2025

---

## Overview

All components run on **one laptop**:

| Component | Runs On |
|-----------|---------|
| Edge gateway (Python) | Laptop |
| Backend (FastAPI) | Laptop |
| PostgreSQL | Laptop |
| React dashboard | Laptop (dev server) or browser |

---

## Hardware Needed

| Item | Notes |
|------|-------|
| **Laptop** | 4+ GB RAM; Windows, macOS, or Linux |
| **USB BLE dongle** | Only if laptop has no built-in Bluetooth |
| **ESP32 wearable(s)** | Per worker |

**No Raspberry Pi required.**

---

## Software Stack (All on Laptop)

| Service | Technology |
|---------|------------|
| Edge | Python 3.10+ (bleak, scikit-learn) |
| Backend | FastAPI + Uvicorn |
| Database | PostgreSQL (local or Docker) |
| Dashboard | React (Vite dev server) |

---

## Cost Impact

| Setup | Cost (INR) |
|-------|------------|
| 1 wearable + laptop | ₹750–₹1,650 |
| 5 wearables + laptop | ₹2,250–₹6,650 |

*(Laptop assumed existing; only BLE dongle if needed.)*

---

## Quick Start

1. Install Python 3.10+, Node.js, PostgreSQL (or Docker).
2. Run backend: `cd backend && uvicorn app.main:app`
3. Run edge: `cd edge && python -m src.main`
4. Run dashboard: `cd dashboard && npm run dev`
5. Connect ESP32 via BLE; open dashboard in browser.

---

## Related Documents

- `TECHNICAL_STACK_CLARIFIED.md` — Full stack with laptop-only section
- `TECHNICAL_STACK_SPEC.md` — Updated for laptop deployment
- `IMPLEMENTATION_PLAN.md` — Step-by-step implementation
