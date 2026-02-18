# Showcase Dashboard — Status

**Last updated:** 2026-02-12

---

## ✅ Done (Phases A–D)

| Phase | Delivered |
|-------|-----------|
| **A** | Tabs (All / Working / Idle / At risk) with counts, Alerts KPI, worker badges (Working/Idle/At risk), alerts “last updated” |
| **B** | State distribution donut, activity timeline (last 10 min), alerts trend chart; event buffer in `useWebSocket` |
| **C** | Edge sends sensor snapshot (temp, accel_mag); backend `POST /api/live/sensor`; dashboard Live sensor strip |
| **D** | “Live Overview” title + subtitle, KPI/chart tooltips, responsive grids, toast on new alert, sidebar “Live Overview” |

---

## Optional / Not Done (by design)

- **Temp line chart (C.4)** — Plan marked optional; not implemented. Can add later if needed.
- **Phase 6 (DASHBOARD_ENHANCEMENT_PLAN)** — Accessibility: focus states, ARIA, `prefers-reduced-motion`, favicon. Optional for showcase.

---

## Errors / Linting

- **Linter:** No errors in dashboard, edge, or backend (last check).
- **No TODO/FIXME** left in the modified files.

---

## Small Consistency Fix

- **Sidebar:** Label updated from “Live View” to “Live Overview” to match the page title.

---

## Before You Demo

1. **Run order:** Postgres → Backend → Edge → Dashboard (see `RUN_ORDER.md`).
2. **Login:** `admin` / `admin123` (or run `python seed_user.py` if needed).
3. **With hardware:** Set `BLE_DEVICE_ID` in `edge/.env`; ensure ESP32 is advertising.
4. **Without hardware:** Leave `BLE_DEVICE_ID` empty; edge uses simulator and dashboard still shows live data.

---

## If You Want to Enhance Further

| Item | Effort | Notes |
|------|--------|--------|
| Temp line chart (last 10 min per worker) | Low | Buffer sensor in hook; Recharts line |
| Accessibility (Phase 6) | Medium | Focus rings, ARIA on alerts, reduced-motion |
| Favicon + meta title | Low | `index.html` + `public/favicon.ico` |
| Sessions list auto-refresh | Low | `useEffect` + interval to refetch |
