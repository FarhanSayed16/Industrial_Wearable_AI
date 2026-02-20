/**
 * Industrial Wearable AI — Live View
 * Worker cards: live state from WebSocket + sample workers from API (W02–W08 with 45d history).
 */
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { motion } from "framer-motion";
import { Radio, Search } from "lucide-react";
import toast from "react-hot-toast";
import { getWorkers } from "../api/workers";
import AlertsPanel from "../components/AlertsPanel";
import EmptyState from "../components/EmptyState";
import Filters from "../components/Filters";
import LiveSensorStrip from "../components/LiveSensorStrip";
import ActivityTimelineChart from "../components/charts/ActivityTimelineChart";
import AlertsTrendChart from "../components/charts/AlertsTrendChart";
import KpiCard from "../components/charts/KpiCard";
import StateDonutLive from "../components/charts/StateDonutLive";
import WorkerCard from "../components/WorkerCard";
import type { WorkerState } from "../hooks/useWebSocket";
import { useWebSocket } from "../hooks/useWebSocket";

type SortBy = "name" | "state" | "updated";
type ViewTab = "all" | "working" | "idle" | "at_risk";

const WORKING_STATES = ["sewing", "adjusting"];
const IDLE_STATES = ["idle", "break", "error"];

function isWorking(state: string) {
  return WORKING_STATES.includes(state);
}
function isIdle(state: string) {
  return IDLE_STATES.includes(state);
}
function isAtRisk(w: { risk_ergo?: boolean; risk_fatigue?: boolean }) {
  return !!(w.risk_ergo || w.risk_fatigue);
}

export type DisplayWorker = WorkerState & { isSample?: boolean };

export default function LiveView() {
  const { workers: liveWorkers, connected, activityTimeline, sensorByWorker, mpuConnectedByWorker } = useWebSocket();
  const [apiWorkers, setApiWorkers] = useState<{ id: string; name: string }[]>([]);
  const [workersLoading, setWorkersLoading] = useState(true);
  const [viewTab, setViewTab] = useState<ViewTab>("all");
  const [stateFilter, setStateFilter] = useState<"all" | "idle" | "sewing" | "adjusting" | "error">("all");
  const [riskFilter, setRiskFilter] = useState<"all" | "at_risk" | "ok">("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [sortBy, setSortBy] = useState<SortBy>("name");

  const fetchWorkers = useCallback(async () => {
    try {
      const list = await getWorkers();
      setApiWorkers(list.map((w) => ({ id: w.id, name: w.name })));
    } catch {
      setApiWorkers([]);
    } finally {
      setWorkersLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchWorkers();
  }, [fetchWorkers]);

  const workers: DisplayWorker[] = useMemo(() => {
    const liveByKey = Object.fromEntries(liveWorkers.map((w) => [w.worker_id, w]));
    return apiWorkers.map((api) => {
      const live = liveByKey[api.name];
      return {
        worker_id: api.name,
        name: api.name,
        current_state: live?.current_state ?? "idle",
        risk_ergo: live?.risk_ergo ?? false,
        risk_fatigue: live?.risk_fatigue ?? false,
        updated_at: live?.updated_at ?? 0,
        isSample: !live,
      };
    });
  }, [apiWorkers, liveWorkers]);

  const liveOnly = useMemo(() => workers.filter((w) => !w.isSample), [workers]);
  const sampleOnly = useMemo(() => workers.filter((w) => w.isSample), [workers]);

  const filteredLive = useMemo(() => {
    const list = liveOnly.filter((w) => {
      if (viewTab === "working" && !isWorking(w.current_state)) return false;
      if (viewTab === "idle" && !isIdle(w.current_state)) return false;
      if (viewTab === "at_risk" && !isAtRisk(w)) return false;
      if (stateFilter !== "all" && w.current_state !== stateFilter) return false;
      if (riskFilter === "at_risk" && !isAtRisk(w)) return false;
      if (riskFilter === "ok" && isAtRisk(w)) return false;
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase().trim();
        if (!w.name.toLowerCase().includes(q) && !w.worker_id.toLowerCase().includes(q)) return false;
      }
      return true;
    });
    return [...list].sort((a, b) => (sortBy === "name" ? a.name.localeCompare(b.name) : sortBy === "updated" ? (b.updated_at ?? 0) - (a.updated_at ?? 0) : a.current_state.localeCompare(b.current_state)));
  }, [liveOnly, viewTab, stateFilter, riskFilter, searchQuery, sortBy]);

  const filteredSample = useMemo(() => {
    const list = sampleOnly.filter((w) => {
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase().trim();
        if (!w.name.toLowerCase().includes(q) && !w.worker_id.toLowerCase().includes(q)) return false;
      }
      return true;
    });
    return [...list].sort((a, b) => a.name.localeCompare(b.name));
  }, [sampleOnly, searchQuery]);

  const kpisLive = useMemo(() => {
    const working = liveOnly.filter((w) => isWorking(w.current_state)).length;
    const idle = liveOnly.filter((w) => isIdle(w.current_state)).length;
    const atRisk = liveOnly.filter((w) => isAtRisk(w)).length;
    return { live: liveOnly.length, working, idle, atRisk, alerts: atRisk };
  }, [liveOnly]);

  const lastUpdate = useMemo(() => {
    if (liveOnly.length === 0) return 0;
    return Math.max(...liveOnly.map((w) => w.updated_at ?? 0));
  }, [liveOnly]);

  const prevAtRiskRef = useRef<Set<string>>(new Set());
  useEffect(() => {
    const atRiskIds = new Set(liveOnly.filter((w) => isAtRisk(w)).map((w) => w.worker_id));
    const prev = prevAtRiskRef.current;
    const added = [...atRiskIds].filter((id) => !prev.has(id));
    if (added.length > 0 && prev.size > 0) {
      toast("New alert: worker(s) at risk", { icon: "⚠️", style: { borderLeft: "4px solid var(--color-error)" } });
    }
    prevAtRiskRef.current = atRiskIds;
  }, [liveOnly]);

  return (
    <div className="live-overview-page">
      <p className="live-overview-subtitle">
        Real-time workers and alerts from wearables
      </p>

      {workersLoading ? (
        <div className="empty-state">
          <p className="empty-state-message">Loading workers…</p>
        </div>
      ) : workers.length === 0 ? (
        <EmptyState
          icon={<Radio />}
          title={connected ? "No workers yet" : "Disconnected"}
          message={
            connected
              ? "Start the edge gateway to see live data, or run the demo seed to load sample workers."
              : "Start the backend and refresh this page."
          }
        />
      ) : (
        <>
          {/* KPIs: Live data first, then sample count */}
          <div className="kpi-cards">
            <KpiCard label="Live" value={kpisLive.live} color="var(--color-primary)" title="Workers with live feed from wearables" />
            <KpiCard label="Working" value={kpisLive.working} color="var(--color-success)" title="Live: sewing or adjusting" />
            <KpiCard label="Idle" value={kpisLive.idle} color="var(--color-idle)" title="Live: idle, break, or error" />
            <KpiCard label="At Risk" value={kpisLive.atRisk} color="var(--color-error)" title="Live: ergonomics or fatigue risk" />
            <KpiCard label="Sample" value={sampleOnly.length} title="Demo workers with historical data only" />
          </div>

          <AlertsPanel workers={liveOnly} />

          {liveOnly.length > 0 && liveOnly.some((w) => mpuConnectedByWorker[w.worker_id] === false) && (
            <div className="no-mpu-banner" role="status">No MPU connected</div>
          )}

          {/* ——— Live now ——— */}
          <section className="live-section" aria-labelledby="live-now-heading">
            <h2 id="live-now-heading" className="live-section-heading">
              Live now
              {liveOnly.length > 0 && (
                <span className="live-section-meta">
                  {lastUpdate
                    ? (() => {
                      const sec = (Date.now() - lastUpdate) / 1000;
                      const ago = sec < 10 ? "just now" : sec < 60 ? `${Math.floor(sec)}s ago` : `${Math.floor(sec / 60)}m ago`;
                      return <>last update {ago}</>;
                    })()
                    : "—"}
                </span>
              )}
            </h2>
            {liveOnly.length === 0 ? (
              <p className="live-section-empty">No live feed. Start the edge gateway with a wearable to see real-time data here.</p>
            ) : (
              <>
                <LiveSensorStrip workers={liveOnly} sensorByWorker={sensorByWorker} />
                <div className="live-view-toolbar live-view-toolbar--compact">
                  <div className="search-wrap">
                    <Search size={16} className="search-icon" />
                    <input
                      type="search"
                      placeholder="Search workers..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="search-input"
                      aria-label="Search workers"
                    />
                  </div>
                  <div className="sort-wrap">
                    <label htmlFor="sort-workers">Sort:</label>
                    <select id="sort-workers" value={sortBy} onChange={(e) => setSortBy(e.target.value as SortBy)} className="sort-select">
                      <option value="name">Name</option>
                      <option value="state">State</option>
                      <option value="updated">Last updated</option>
                    </select>
                  </div>
                </div>
                <Filters stateFilter={stateFilter} riskFilter={riskFilter} onStateChange={setStateFilter} onRiskChange={setRiskFilter} />
                <div className="live-view-tabs" role="tablist">
                  {(["all", "working", "idle", "at_risk"] as const).map((tab) => (
                    <button
                      key={tab}
                      type="button"
                      role="tab"
                      aria-selected={viewTab === tab}
                      className={`live-view-tab ${viewTab === tab ? "live-view-tab-active" : ""}`}
                      onClick={() => setViewTab(tab)}
                    >
                      {tab === "all" ? "All" : tab === "working" ? "Working" : tab === "idle" ? "Idle" : "At risk"}
                      <span className="live-view-tab-count">
                        ({tab === "all" ? liveOnly.length : tab === "working" ? kpisLive.working : tab === "idle" ? kpisLive.idle : kpisLive.atRisk})
                      </span>
                    </button>
                  ))}
                </div>
                <motion.div className="worker-cards-grid worker-cards-grid--live" initial="hidden" animate="visible" variants={{ visible: { transition: { staggerChildren: 0.05 } }, hidden: {} }}>
                  {filteredLive.map((w) => (
                    <motion.div key={w.worker_id} variants={{ visible: { opacity: 1, y: 0 }, hidden: { opacity: 0, y: 12 } }} transition={{ duration: 0.25 }}>
                      <WorkerCard {...w} isSample={false} />
                    </motion.div>
                  ))}
                </motion.div>
              </>
            )}
          </section>

          {/* ——— Sample workers (demo) ——— */}
          {sampleOnly.length > 0 && (
            <section className="live-section live-section--sample" aria-labelledby="sample-heading">
              <h2 id="sample-heading" className="live-section-heading live-section-heading--muted">
                Sample workers (historical data for demo)
              </h2>
              <motion.div className="worker-cards-grid" initial="hidden" animate="visible" variants={{ visible: { transition: { staggerChildren: 0.03 } }, hidden: {} }}>
                {filteredSample.map((w) => (
                  <motion.div key={w.worker_id} variants={{ visible: { opacity: 1, y: 0 }, hidden: { opacity: 0, y: 8 } }} transition={{ duration: 0.2 }}>
                    <WorkerCard {...w} isSample />
                  </motion.div>
                ))}
              </motion.div>
            </section>
          )}

          {/* ——— Charts (live feed only) ——— */}
          <section className="live-charts-section" aria-labelledby="charts-heading">
            <h2 id="charts-heading" className="live-section-heading live-section-heading--muted">Charts (live feed)</h2>
            <div className="live-charts-grid">
              <div className="live-chart-card">
                <StateDonutLive workers={workers} />
              </div>
              <div className="live-chart-card">
                <ActivityTimelineChart events={activityTimeline} />
              </div>
              <div className="live-chart-card">
                <AlertsTrendChart events={activityTimeline} />
              </div>
            </div>
          </section>
        </>
      )}
    </div>
  );
}
