# Architecture Diagrams — PlantUML Index

All architecture and flow diagrams for **Industrial Wearable AI** are split into **one file per diagram** in **`docs/diagrams/`**.

## Diagram List (One File Each)

| # | File | Description |
|---|------|-------------|
| 1 | **01-system-architecture-high-level.puml** | High-level system: Worker → Wearable → Edge → Backend → Dashboard (components + actors). |
| 2 | **02-deployment-diagram.puml** | Deployment: Wearable device, Edge (RPi), Backend server, Browser; BLE/HTTP/WebSocket links. |
| 3 | **03-sequence-end-to-end-data-flow.puml** | End-to-end sequence: Worker wears band → BLE → Edge → Backend → DB → Dashboard → Supervisor. |
| 4 | **04-sequence-edge-processing-pipeline.puml** | Edge pipeline sequence: BLE → Ingest → Filter → Segment → Features → Model → Rules → POST API. |
| 5 | **05-sequence-dashboard-live-update.puml** | Dashboard live update: Supervisor opens app → WebSocket → Backend stores events → broadcast → UI update. |
| 6 | **06-activity-end-to-end-pipeline.puml** | End-to-end activity flow: sample → BLE → edge process → backend store → dashboard (repeat). |
| 7 | **07-activity-edge-processing-detail.puml** | Edge processing detail: receive → validate → buffer → window → features → model → rules → POST. |
| 8 | **08-state-activity-states.puml** | Activity state machine: Sewing, Idle, Adjusting, Error, Break (transitions). |
| 9 | **09-state-risk-states.puml** | Risk state machine: Normal, Ergonomic Risk, Fatigue Risk. |
| 10 | **10-use-case-diagram.puml** | Use cases: Worker (wear, stream), Supervisor (live view, alerts, summary), Owner (manage, trends). |
| 11 | **11-class-backend-entities.puml** | Backend entities: Worker, Device, Session, ActivityEvent, SessionAggregate (relationships). |
| 12 | **12-component-detailed.puml** | Detailed components: Wearable (firmware, IMU, BLE), Edge (ingest, filter, model, rules), Backend (API, WS, DB), Dashboard (views). |
| 13 | **13-data-flow-dfd-style.puml** | DFD-style: processes (Wearable, Edge, Backend, Dashboard) and data stores (activity_events, session_aggregates). |
| 14 | **14-c4-context-simplified.puml** | C4 context: people (Worker, Supervisor) and systems (Wearable, Edge, Backend, Dashboard). |
| 15 | **15-ml-training-flow.puml** | ML flow: Offline (collect → label → features → train → export joblib) → Edge (load model → inference). |

**Location:** `docs/diagrams/` (15 `.puml` files)

**Legacy:** The single combined file is still available at **`docs/architecture-diagrams.puml`** (all 15 diagrams in one file).

## How to Render

### Option 1: PlantUML CLI (one diagram per file)

Each diagram is already in its own file under `docs/diagrams/`. Render one or all:

```bash
# Render one diagram (e.g. first)
plantuml -tpng docs/diagrams/01-system-architecture-high-level.puml

# Render all 15 diagrams
plantuml -tpng docs/diagrams/*.puml

# Or SVG
plantuml -tsvg docs/diagrams/*.puml
```

### Option 2: VS Code

- Install extension **PlantUML** (jebbs.plantuml).
- Open any file in `docs/diagrams/` (e.g. `01-system-architecture-high-level.puml`).
- Use **“Export Current Diagram”** or **“Preview Current Diagram”** (Alt+D).

### Option 3: Online

- Open any file from `docs/diagrams/`, copy its full content, and paste into [PlantUML Online](https://www.plantuml.com/plantuml/uml).

## File Location

- **One diagram per file (15 files):** `docs/diagrams/01-system-architecture-high-level.puml` … `docs/diagrams/15-ml-training-flow.puml`
- **Single file (all 15 in one):** `docs/architecture-diagrams.puml`
- **This index:** `docs/ARCHITECTURE_DIAGRAMS_README.md`
