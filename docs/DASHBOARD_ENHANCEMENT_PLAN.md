# Dashboard Enhancement Plan — Industrial Wearable AI

**Document:** Complete plan to transform the dashboard into a professional, animated, data-rich UI.  
**Version:** 1.0  
**Last updated:** 2025-02-09

---

## Current State

| Component | Status |
|-----------|--------|
| Login | Basic form, no styling |
| Live View | Worker cards, filters, AlertsPanel — inline styles |
| Sessions | Table + list — inline styles |
| Layout | No sidebar, no consistent nav |
| Design | No design system, mixed light/dark |
| Charts | Recharts installed but **unused** |
| Animations | None |
| Typography | System fonts |

---

## Enhancement Phases

### Phase 0: Foundation & Design System

**Goal:** Establish design tokens, theme, and base infrastructure.

| Task | Details |
|------|---------|
| 0.1 Design tokens | Create CSS variables: `--color-primary`, `--color-success`, `--color-warning`, `--color-error`, `--radius-sm/md/lg`, `--shadow-sm/md/lg`, `--transition-fast/normal/slow` |
| 0.2 Theme | Light theme (primary: industrial teal/blue); optional dark mode toggle |
| 0.3 Typography | Pick a font (e.g. **Inter** or **DM Sans**); headings, body, captions |
| 0.4 Remove conflicting styles | Clean `index.css` and `App.css`; centralize in `theme.css` |
| 0.5 Animation library | Add **framer-motion** for enter/exit and micro-interactions |

**Files:** `src/theme.css`, `src/index.css`, `package.json` (framer-motion)

**Status:** ✅ Complete (2025-02-09)

---

### Phase 1: Layout & Navigation

**Goal:** Consistent app shell with sidebar and nav.

| Task | Details |
|------|---------|
| 1.1 App shell | Fixed sidebar (collapsible on mobile) + main content area |
| 1.2 Sidebar nav | Links: Live View, Shift Summary, Logout |
| 1.3 Header | Page title, connection status, user menu |
| 1.4 Breadcrumbs | Optional for Sessions page |
| 1.5 Responsive | Mobile: hamburger menu; Desktop: full sidebar |

**Files:** `src/components/Layout.tsx`, `src/components/Sidebar.tsx`, `src/components/Header.tsx`, update `App.tsx`

**Status:** ✅ Complete (2025-02-09)

---

### Phase 2: Visual Design & Animations

**Goal:** Polished look and smooth motion.

| Task | Details |
|------|---------|
| 2.1 Cards | Glassmorphism or subtle gradient; soft shadow; hover lift |
| 2.2 Buttons | Primary, secondary, ghost; loading state; ripple/scale on click |
| 2.3 Inputs | Styled selects, inputs; focus ring; error state |
| 2.4 Page transitions | Fade/slide when switching routes |
| 2.5 Card enter animations | Staggered fade-in for worker cards |
| 2.6 Connection badge | Pulse when connected; shake when disconnected |
| 2.7 State badge | Smooth color transition on state change |
| 2.8 Loading states | Skeleton loaders instead of "Loading..." text |

**Libraries:** framer-motion

**Status:** ✅ Complete (2025-02-09)

---

### Phase 3: Charts & Data Visualization

**Goal:** Use Recharts for insights.

| Task | Details |
|------|---------|
| 3.1 Session summary chart | Donut/pie for activity breakdown (active_pct, idle_pct, etc.) |
| 3.2 Live view stats | Small KPI cards: total workers, active, idle, at risk |
| 3.3 Session list enhancement | Bar or mini-chart per session showing activity mix |
| 3.4 Alerts trend | Optional: simple line/sparkline for alert count over time |
| 3.5 Chart animations | Recharts built-in animations; configure duration |

**Files:** `src/components/charts/ActivityDonut.tsx`, `src/components/charts/SessionBar.tsx`, update `Sessions.tsx`, `LiveView.tsx`

**Status:** ✅ Complete (2025-02-09) — ActivityDonut + KPI cards implemented. Session list mini-chart skipped (requires per-session summary fetch).

---

### Phase 4: Component Enhancements

**Goal:** Better components per page.

| Task | Details |
|------|---------|
| 4.1 Login page | Centered card, logo, gradient bg, input animations, remember me |
| 4.2 Worker card | Avatar/icon, progress ring for "activity level", tooltip on hover |
| 4.3 Alerts panel | Animated list; severity indicator; expand/collapse |
| 4.4 Filters | Styled dropdowns or pill buttons; clear filters |
| 4.5 Empty states | Illustration or icon + helpful message |
| 4.6 Error states | Retry button, friendly copy |
| 4.7 Toast styling | Match theme; position, duration |

**Status:** ✅ Complete (2025-02-09)

---

### Phase 5: UX Improvements

**Goal:** Smoother workflows.

| Task | Details |
|------|---------|
| 5.1 Auto-refresh | Sessions list refresh every N seconds (optional) |
| 5.2 Keyboard shortcuts | `Esc` to close modals; `?` for help |
| 5.3 Search | Search workers by name on Live View |
| 5.4 Sort | Sort workers by state, name, last updated |
| 5.5 Session date filter | Filter sessions by date range |
| 5.6 Confirmation on logout | Modal or toast |

**Status:** ✅ Complete (2025-02-09)

---

### Phase 6: Polish & Accessibility

| Task | Details |
|------|---------|
| 6.1 Focus management | Visible focus states; tab order |
| 6.2 ARIA labels | Buttons, links, live regions for alerts |
| 6.3 Reduced motion | Respect `prefers-reduced-motion` |
| 6.4 Color contrast | WCAG AA for text |
| 6.5 Favicon & meta | Industrial Wearable AI branding |

---

## Suggested Color Palette

| Token | Light | Dark (optional) |
|-------|-------|-----------------|
| Primary | `#0d9488` (teal) | `#14b8a6` |
| Success | `#22c55e` | `#4ade80` |
| Warning | `#f59e0b` | `#fbbf24` |
| Error | `#ef4444` | `#f87171` |
| Idle | `#94a3b8` | `#94a3b8` |
| Background | `#f8fafc` | `#0f172a` |
| Card | `#ffffff` | `#1e293b` |

---

## Suggested Dependencies

| Package | Purpose |
|---------|---------|
| `framer-motion` | Animations |
| `lucide-react` or `react-icons` | Icons |
| (Optional) `tailwindcss` | Utility-first CSS — only if you want to adopt it |
| (Optional) `@radix-ui/react-*` | Accessible primitives (dropdown, dialog) |

---

## File Structure (After Enhancement)

```
dashboard/src/
├── components/
│   ├── Layout.tsx
│   ├── Sidebar.tsx
│   ├── Header.tsx
│   ├── AlertsPanel.tsx
│   ├── WorkerCard.tsx
│   ├── charts/
│   │   ├── ActivityDonut.tsx
│   │   └── SessionBar.tsx
│   └── ui/
│       ├── Button.tsx
│       ├── Card.tsx
│       ├── Select.tsx
│       └── Skeleton.tsx
├── pages/
│   ├── Login.tsx
│   ├── LiveView.tsx
│   └── Sessions.tsx
├── hooks/
│   └── useWebSocket.ts
├── theme.css
├── index.css
└── App.tsx
```

---

## Implementation Order

1. **Phase 0** — Foundation (1–2 days)
2. **Phase 1** — Layout & Nav (0.5–1 day)
3. **Phase 2** — Visual Design & Animations (1–2 days)
4. **Phase 4** — Component enhancements (in parallel with 2)
5. **Phase 3** — Charts (1 day)
6. **Phase 5** — UX (0.5–1 day)
7. **Phase 6** — Polish (0.5 day)

**Total estimate:** 5–8 days for full implementation.

---

## Priority Quick Wins (If Time Limited)

| Priority | Task | Impact |
|----------|------|--------|
| 1 | Add Layout + Sidebar | Major structure improvement |
| 2 | Add framer-motion + card animations | High visual impact |
| 3 | Activity donut chart on Sessions | Use existing Recharts |
| 4 | Login page redesign | Strong first impression |
| 5 | KPI cards on Live View | Data at a glance |

---

## Reference Documents

- `MASTER_PLAN.md` — Project phases
- `PROJECT_STATUS_AND_ARCHITECTURE.md` — System overview
