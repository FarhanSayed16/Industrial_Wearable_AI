# Industrial Wearable AI — UML Diagrams (PlantUML)

This folder contains PlantUML source files for all main UML diagrams of the project. They use a shared theme (teal/blue palette, clean layout) for a professional look.

---

## Diagram Index

| # | File | Diagram Type | Description |
|---|------|--------------|-------------|
| 0 | `00-context.puml` | **System Context** | High-level C4-style context: actors (Worker, Supervisor) and main system blocks (Wearable, Edge, Backend, Dashboard). |
| 1 | `01-use-case.puml` | **Use Case** | Use cases for Worker, Supervisor, and System: wear device, stream data, classify, post events, login, view live overview, alerts, history, charts. |
| 2 | `02-component.puml` | **Component** | Components inside Wearable (firmware, IMU, BLE, JSON), Edge (BLE client, buffer, pipeline, feature extractor, classifier, API client), Backend (REST, WebSocket, event service, DB), Dashboard (auth, live view, sessions, hook, charts). |
| 3 | `03-deployment.puml` | **Deployment** | Deployment nodes: Wearable device (ESP32), Laptop (Edge + Backend + Dashboard processes), PostgreSQL; actors and connections. |
| 4 | `04-sequence-data-flow.puml` | **Sequence** | Data flow: Wearable → Edge (BLE samples) → buffer → classify → POST events → Backend → DB → WebSocket → Dashboard; sensor snapshot. |
| 5 | `05-sequence-login-websocket.puml` | **Sequence** | Login flow and WebSocket: login request, token, GET workers, WebSocket connect, live state and sensor messages. |
| 6 | `06-class-domain.puml` | **Class** | Domain model (backend entities): User, Worker, Device, Session, ActivityEvent, SessionAggregate, ActivityLabel enum and relationships. |
| 7 | `07-activity-edge-pipeline.puml` | **Activity** | Edge pipeline: receive sample → buffer → window → filter → features → classify → batch → POST events; device-status and sensor. |
| 8 | `08-state-activity.puml` | **State** | Worker activity state machine: sewing, idle, adjusting, error, break; transitions from classifier output. |

**Theme:** `theme.puml` — shared `skinparam` (colors, fonts, borders). Other diagrams can `!include theme.puml` for consistency.

---

## How to Generate Images

### Option 1: PlantUML CLI (Java)

1. Install [PlantUML](https://plantuml.com/download) (requires Java).
2. From this folder:

```bash
cd docs/uml
plantuml -tpng *.puml
# or for SVG:
plantuml -tsvg *.puml
```

Output: `01-use-case.png`, `02-component.png`, etc., in the same folder.

### Option 2: VS Code / Cursor

1. Install extension **PlantUML** (jebbs.plantuml).
2. Open a `.puml` file and press `Alt+D` (or use “Preview Current Diagram”) to preview.
3. Export from the preview (right-click → Export) to PNG/SVG.

### Option 3: Online

1. Copy the contents of a `.puml` file.
2. Paste at [PlantUML Online Server](https://www.plantuml.com/plantuml/uml/).
3. Download the rendered image.

### Option 4: Pandoc / Doc

To embed in a document (e.g. research paper), generate PNG or SVG and reference them:

```markdown
![Use Case](uml/01-use-case.png)
```

**Research paper (`docs/RESEARCH_PAPER.md`):** The paper includes placeholders for figures and tables. You can put rendered diagrams in `docs/figures/` (create the folder if needed) and update the figure references. Mapping: Fig. 1 ← `00-context` or `02-component`; Fig. 2 ← `08-state-activity`; Fig. 3 ← `07-activity-edge-pipeline`; Fig. 4 ← `01-use-case`; Fig. 5 ← `03-deployment`; Fig. 6 ← `04-sequence-data-flow`; Fig. 7 ← `06-class-domain`; Fig. 8 ← dashboard screenshot (no UML).

---

## Color Palette (Theme)

| Use | Hex | Description |
|-----|-----|-------------|
| Primary | `#0d9488` | Teal — borders, main elements |
| Secondary | `#1e40af` | Blue — actors, DB, links |
| Background (light) | `#F8FAFC` | Page background |
| Component fill | `#F0FDFA` | Teal tint |
| Actor fill | `#EFF6FF` | Blue tint |
| Muted | `#64748b` | Arrows, secondary text |
| Success | `#22c55e` / `#DCFCE7` | e.g. sewing state |
| Warning | `#f59e0b` / `#FEF3C7` | e.g. break, diamonds |
| Error | `#ef4444` / `#FEE2E2` | e.g. error state |

---

## File Naming

- `00-context.puml` — context diagram (no dependency on others).
- `01-use-case.puml` … `08-state-activity.puml` — numbered for order in docs.
- `theme.puml` — include-only (no `@startuml`), shared styling.

All diagrams are self-contained except for `!include theme.puml`; if the include path fails, copy the `skinparam` block from `theme.puml` into each file.
