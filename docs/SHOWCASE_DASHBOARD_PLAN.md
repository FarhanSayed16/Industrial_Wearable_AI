# Showcase Dashboard Plan — Industrial Wearable AI

**Purpose:** Plan for a single, informative Live dashboard that shows all workers (active/inactive, working/non-working), alerts, movement stats from ESP32, graphs, temperature, and clear UI/UX for project showcase.  
**Last updated:** 2026-02-12

---

## 1. What We Have Today

| Data source | What we get | Where it shows |
|-------------|-------------|----------------|
| **ESP32 → BLE** | Raw samples: `ts`, `ax`, `ay`, `az`, `gx`, `gy`, `gz`, `temp` | Edge only (not sent to backend) |
| **Edge → Backend** | Inferred events: `ts`, `label` (sewing/idle/adjusting/error/break), `risk_ergo`, `risk_fatigue` | Stored in DB; last state broadcast via WebSocket |
| **Backend → Dashboard** | Live: worker_id, name, current_state, risk_ergo, risk_fatigue, updated_at | Live View: worker cards, KPIs, Alerts panel |
| **Sessions API** | Per-session: active_pct, idle_pct, adjusting_pct, error_pct, alert_count | Shift Summary page: donut + table |

**Gap for showcase:** Temperature and raw movement (accel/gyro) are **not** sent to the backend today — only the classified activity and risks. To show “stats of worker movement” and “temp” on the dashboard, we need to stream a **live sensor snapshot** from edge to backend and then to the dashboard.

---

## 2. What to Show on the Live Dashboard (Showcase Goals)

### 2.1 Worker overview (clear categories)

- **All workers** — single list/grid with clear status.
- **Active / Working** — state = sewing (or adjusting if you count that as “working”).
- **Inactive / Non-working** — state = idle, break, or error.
- **At risk** — risk_ergo or risk_fatigue = true (subset of workers).
- **Last seen** — time since last update per worker (online vs stale).

**UI:** Tabs or filter chips: **All | Working | Idle / Non-working | At risk**, with counts. Default view can be “All” with badges (Working / Idle / At risk) on each card.

### 2.2 Alerts

- **All alerts** — every worker with risk_ergo or risk_fatigue.
- **Severity** — e.g. high (both ergo + fatigue), medium (one of them).
- **Who & why** — worker name, “Ergonomics”, “Fatigue”, and optionally “last raised” time.

**UI:** Alerts panel at top (existing), expandable list; optional “Alert count” KPI and small “Alerts in last 5 min” trend.

### 2.3 Stats from ESP32 (movement + temp)

- **Temperature** — last reported temp per worker (°C), e.g. “28.5 °C”.
- **Movement** — simple metric from accelerometer (e.g. magnitude or “low / medium / high”) so you can say “worker movement from ESP”.
- **Last sensor update** — timestamp so it’s clear data is live from device.

**Requirement:** Edge must send a **live sensor payload** (e.g. every few seconds) to the backend; backend broadcasts it (e.g. same WebSocket or separate channel) so the dashboard can show it.

### 2.4 Graphs and trends

- **Activity over time (live)** — last 5–10 minutes: for each worker (or “all”), show state over time (e.g. sewing / idle as a stepped line or stacked area). Uses live events or a short-lived buffer.
- **State distribution (right now)** — pie/donut: share of workers in sewing / idle / adjusting / break / error. Reuses existing donut component with live data.
- **Alerts over time** — count of “at risk” events in last N minutes (sparkline or bar per minute).
- **Temperature (optional)** — line chart: temp per worker over last 10–15 min (needs sensor stream).

### 2.5 KPIs and summary

- **Total workers** (with live data).
- **Active** — sewing (and optionally adjusting).
- **Idle / Non-working** — idle + break + error.
- **At risk** — count of workers with any risk.
- **Live feed status** — “Live” with last update time (already added).

**UI:** Top row of KPI cards; below that Alerts → Live sensor strip (if we add it) → Graphs → Worker grid.

---

## 3. Proposed Live Page Structure (UI/UX)

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Live Overview                                    [WebSocket: Connected]  │
├─────────────────────────────────────────────────────────────────────────┤
│  [ Total: 4 ]  [ Working: 2 ]  [ Idle: 1 ]  [ At risk: 1 ]  [ Alerts: 2 ] │
├─────────────────────────────────────────────────────────────────────────┤
│  ▼ Active Alerts (2)                                                     │
│     • W01 — Fatigue                    • W02 — Ergonomics                │
├─────────────────────────────────────────────────────────────────────────┤
│  Live sensor (from ESP32)  [optional]                                    │
│  W01: Temp 29.2 °C  •  Movement: medium  •  Updated 2s ago               │
├─────────────────────────────────────────────────────────────────────────┤
│  [ All | Working | Idle / Non-working | At risk ]   Search...  Sort: name │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │ W01         │  │ W02         │  │ W03         │  │ W04         │     │
│  │ sewing      │  │ idle        │  │ adjusting   │  │ sewing      │     │
│  │ ⚠ Fatigue   │  │             │  │             │  │             │     │
│  │ Updated 1m  │  │ Updated 5m   │  │ Updated 2m  │  │ Updated 30s │     │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘     │
├─────────────────────────────────────────────────────────────────────────┤
│  Activity (last 10 min)          │  State distribution (now)             │
│  [Line/area chart by state]      │  [Donut: sewing / idle / …]            │
├─────────────────────────────────────────────────────────────────────────┤
│  Alerts trend (last 10 min)      │  [Sparkline or bars]                   │
└─────────────────────────────────────────────────────────────────────────┘
```

- **First screen:** KPIs + Alerts + Worker grid (with Working / Idle / At risk filters) so “all active, inactive, working, non-working, alerts” are visible at a glance.
- **Second row:** Optional live sensor strip (temp + movement) when we have the data.
- **Third row:** Graphs (activity timeline, state donut, alerts trend) for “stats of worker movement” and trends.

---

## 4. Data & Backend Changes Required

### 4.1 Live sensor stream (temp + movement)

| Layer | Change |
|-------|--------|
| **Edge** | Every 2–3 s (or with event batch), send a **sensor snapshot**: `worker_id`, `temp`, `accel_mag` (e.g. sqrt(ax²+ay²+az²) or normalized), `ts`. Either in same POST as events (optional field) or a separate POST, e.g. `POST /api/live/sensor`. |
| **Backend** | New optional endpoint `POST /api/live/sensor` or extend event payload; store or just broadcast latest per worker. Broadcast on WebSocket: e.g. `{ type: "sensor", worker_id, temp, accel_mag, ts }`. |
| **Dashboard** | useWebSocket (or same WS) handles `type: "sensor"`; store last sensor per worker; show “Live sensor” strip and optional temp chart. |

### 4.2 Activity timeline (last N minutes)

- **Option A:** Backend keeps a short-lived buffer of (worker_id, ts, label) for last 10 min; new endpoint `GET /api/live/activity-timeline` returns bucketed counts or events for chart. Dashboard polls every 30 s or so.
- **Option B:** Dashboard buffers incoming WebSocket events (by worker, ts, label) for last 10 min and builds the chart client-side. No backend change.

**Recommendation:** Option B for showcase (simpler); Option A if you want server-authoritative history.

### 4.3 State distribution

- Use existing WebSocket worker list: compute counts by `current_state` and pass to existing donut component. No backend change.

### 4.4 Alerts trend

- Dashboard: keep last N minutes of “alert” events (e.g. when we receive a worker state with risk_ergo or risk_fatigue); bucket by minute and show count. No backend change if we buffer; or backend can expose `GET /api/live/alert-counts?minutes=10` for accuracy.

---

## 5. Implementation Phases (Next Steps)

### Phase A — Live page clarity (no new data)

**Goal:** One screen that clearly shows “all workers, working, non-working, all alerts” for demo.

| Step | Task | Files |
|------|------|--------|
| A.1 | Add filter tabs: **All | Working | Idle / Non-working | At risk** with counts; default All | `LiveView.tsx`, `Filters` or new `WorkerTabs` |
| A.2 | Ensure “Working” = sewing (and optionally adjusting); “Idle / Non-working” = idle, break, error | `LiveView.tsx` |
| A.3 | Add KPI card: **Alerts** (count of workers with risk) | `LiveView.tsx`, `KpiCard` |
| A.4 | Alerts panel: show “last updated” per alert; ensure all alerts listed | `AlertsPanel.tsx` |
| A.5 | Worker card: show “Working” / “Idle” / “At risk” badge so status is obvious | `WorkerCard.tsx` |

**Outcome:** Demo-ready view: “Here are all workers; these are working, these idle, these at risk; these are all current alerts.”

### Phase B — Live graphs (from existing WebSocket data)

**Goal:** Show movement/activity stats and trends from data we already have.

| Step | Task | Files |
|------|------|--------|
| B.1 | **State distribution donut** on Live page — from current `workers` array (count by state) | `LiveView.tsx`, reuse `ActivityDonut` or small donut |
| B.2 | **Activity timeline** — buffer last 10 min of WebSocket updates (worker_id, ts, label) in a hook; render line or stacked area (e.g. Recharts) | New hook `useActivityTimeline`, new `ActivityTimelineChart.tsx` |
| B.3 | **Alerts trend** — buffer “at risk” updates by minute; small sparkline or bar chart “Alerts in last 10 min” | Same buffer or new hook, small chart component |

**Outcome:** “Stats of worker movement” (activity over time) and “all alerts” with a trend.

### Phase C — Live sensor (temp + movement from ESP32)

**Goal:** Show temperature and movement from device.

| Step | Task | Files |
|------|------|--------|
| C.1 | Edge: compute `accel_mag` from last sample; every 2–3 s send `{ worker_id, temp, accel_mag, ts }` to backend (new payload or endpoint) | `edge/src/main.py`, `edge/src/api_client.py` |
| C.2 | Backend: accept sensor snapshot; broadcast on WebSocket (e.g. `type: "sensor"`) | `backend/app/api/events.py` or new `api/live.py`, `websocket_hub` |
| C.3 | Dashboard: handle sensor messages; show “Live sensor” strip: per worker temp, movement (low/med/high from accel_mag), last updated | `useWebSocket.ts` or new hook, `LiveSensorStrip.tsx` |
| C.4 | Optional: temp line chart per worker (last 10 min) | New component, buffer sensor in hook |

**Outcome:** “Temperature and movement from ESP32” visible on Live page.

### Phase D — Polish for showcase

**Goal:** Professional, informative UI.

| Step | Task |
|------|------|
| D.1 | Page title: “Live Overview” or “Command Center”; subtitle: “Real-time workers and alerts from wearables” |
| D.2 | Empty state: “No workers yet” vs “WebSocket disconnected” (already improved) |
| D.3 | Responsive grid: worker cards wrap; graphs stack on small screens |
| D.4 | Tooltips on KPIs (“Working = currently sewing”) and on charts |
| D.5 | Optional: subtle sound or toast when new alert appears |
| D.6 | Sessions page: keep as “Shift Summary”; ensure one click from sidebar |

---

## 6. Suggested Order for Showcase

1. **Phase A** (1–2 days) — Filters, KPIs, badges, alerts clarity. **Do first** so you can demo “all workers, working, idle, at risk, all alerts” without new backend work.
2. **Phase B** (1–2 days) — State donut, activity timeline, alerts trend from existing data. **Do second** for “stats of worker movement” and graphs.
3. **Phase C** (1–2 days) — Sensor stream and temp/movement on dashboard. **Do if time** for “data from ESP” story.
4. **Phase D** (0.5–1 day) — Copy, layout, responsiveness, tooltips. **Do last** for polish.

---

## 7. File Checklist (New/Modified)

| File | Purpose |
|------|---------|
| `dashboard/src/pages/LiveView.tsx` | Tabs/filters (All/Working/Idle/At risk), KPI Alerts, layout for graphs and sensor strip |
| `dashboard/src/components/WorkerCard.tsx` | Badge: Working / Idle / At risk |
| `dashboard/src/components/AlertsPanel.tsx` | Optional “last raised” time; ensure all alerts listed |
| `dashboard/src/hooks/useActivityTimeline.ts` | Buffer last 10 min of (worker_id, ts, label); expose for charts |
| `dashboard/src/components/charts/ActivityTimelineChart.tsx` | Line/area of activity over time |
| `dashboard/src/components/charts/StateDonutLive.tsx` | Donut from current workers (or reuse ActivityDonut with live summary) |
| `dashboard/src/components/LiveSensorStrip.tsx` | Temp + movement per worker (Phase C) |
| `edge/src/main.py` | Send sensor snapshot (temp, accel_mag) to backend (Phase C) |
| `backend/app/api/events.py` or `api/live.py` | Accept sensor snapshot; broadcast via ws_hub (Phase C) |
| `dashboard/src/hooks/useWebSocket.ts` | Handle `type: "sensor"` message; expose lastSensorByWorker (Phase C) |

---

## 8. One-Paragraph “Showcase Story”

**Live Overview** shows every worker connected via wearable: who is **working** (sewing), who is **idle** or on break, and who is **at risk** (ergonomics or fatigue). All **alerts** are listed at the top with severity. **KPIs** (total, active, idle, at risk, alert count) and a **live state donut** give an instant picture; an **activity timeline** and **alerts trend** show how movement and risks evolved over the last minutes. When the sensor stream is enabled, **temperature** and **movement** from the ESP32 appear per worker so the demo clearly shows end-to-end data from device to dashboard.

---

## 9. Reference

- **Current enhancement plan:** `docs/DASHBOARD_ENHANCEMENT_PLAN.md`
- **Run order:** `docs/RUN_ORDER.md`
- **Technical stack (data shapes):** `docs/TECHNICAL_STACK_SPEC.md`
- **Test results:** `docs/TEST_RUN_RESULTS.md`
