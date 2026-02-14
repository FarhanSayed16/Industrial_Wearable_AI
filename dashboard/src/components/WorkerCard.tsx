/**
 * Industrial Wearable AI — Worker Card
 * Phase 4.2: Avatar, progress ring; sample workers get expandable history.
 */
import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { ChevronDown, History, User } from "lucide-react";
import { getWorkerHistory, type WorkerHistoryEntry } from "../api/workers";
import type { WorkerState } from "../hooks/useWebSocket";
import Card from "./ui/Card";

const stateColors: Record<string, string> = {
  sewing: "var(--color-success)",
  idle: "var(--color-idle)",
  adjusting: "var(--color-adjusting)",
  error: "var(--color-error)",
  break: "var(--color-break)",
};

/** Activity level 0–100 derived from state */
function getActivityLevel(state: string): number {
  switch (state) {
    case "sewing": return 100;
    case "adjusting": return 50;
    case "break": return 25;
    default: return 0;
  }
}

function getInitials(name: string, workerId: string): string {
  if (name) {
    const parts = name.trim().split(/\s+/);
    if (parts.length >= 2) {
      return (parts[0][0] + parts[1][0]).toUpperCase();
    }
    return name.slice(0, 2).toUpperCase();
  }
  return String(workerId).slice(0, 2).toUpperCase();
}

function formatUpdatedAt(ts: number): string {
  if (!ts) return "—";
  try {
    const now = Date.now();
    const diff = (now - ts) / 1000;
    if (diff < 60) return "just now";
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    return new Date(ts).toLocaleTimeString();
  } catch {
    return "—";
  }
}

interface WorkerCardProps extends WorkerState {
  /** True when worker is from seed/demo data (no live feed) */
  isSample?: boolean;
}

const WORKING_STATES = ["sewing", "adjusting"];
const IDLE_STATES = ["idle", "break", "error"];

function getStatusBadge(state: string): "working" | "idle" | null {
  if (WORKING_STATES.includes(state)) return "working";
  if (IDLE_STATES.includes(state)) return "idle";
  return null;
}

function formatSessionDate(iso: string): string {
  try {
    const d = new Date(iso);
    return d.toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric", hour: "2-digit", minute: "2-digit" });
  } catch {
    return iso;
  }
}

export default function WorkerCard({
  worker_id,
  name,
  current_state,
  risk_ergo,
  risk_fatigue,
  updated_at,
  isSample,
}: WorkerCardProps) {
  const [historyExpanded, setHistoryExpanded] = useState(false);
  const [history, setHistory] = useState<WorkerHistoryEntry[]>([]);
  const [historyLoading, setHistoryLoading] = useState(false);

  useEffect(() => {
    if (!isSample || !historyExpanded) return;
    setHistoryLoading(true);
    getWorkerHistory(name, 20)
      .then(setHistory)
      .catch(() => setHistory([]))
      .finally(() => setHistoryLoading(false));
  }, [isSample, historyExpanded, name]);

  const stateColor = stateColors[current_state] ?? "var(--color-warning)";
  const activityLevel = getActivityLevel(current_state);
  const initials = getInitials(name, worker_id);
  const statusBadge = getStatusBadge(current_state);

  const tooltipText = [
    `State: ${current_state}`,
    risk_ergo && "Ergonomics risk",
    risk_fatigue && "Fatigue risk",
    `Activity: ${activityLevel}%`,
  ]
    .filter(Boolean)
    .join(" • ");

  return (
    <Card>
      <div
        className="worker-card-content"
        data-worker-id={worker_id}
        title={tooltipText}
      >
        <div className="worker-card-header">
          <div className="worker-avatar">
            <div className="worker-avatar-inner">
              {initials}
            </div>
            <svg className="worker-progress-ring" viewBox="0 0 36 36">
              <circle
                className="worker-progress-bg"
                cx="18"
                cy="18"
                r="15.9"
              />
              <circle
                className="worker-progress-fill"
                cx="18"
                cy="18"
                r="15.9"
                style={{
                  strokeDasharray: "100 100",
                  strokeDashoffset: 100 - activityLevel,
                  stroke: stateColor,
                }}
              />
            </svg>
          </div>
          <div className="worker-card-meta">
            <div className="worker-card-name">{name}</div>
            <div className="worker-card-badges">
              <motion.span
                className="worker-card-state"
                style={{ background: stateColor }}
                initial={false}
                animate={{ backgroundColor: stateColor }}
                transition={{ duration: 0.3 }}
              >
                {current_state}
              </motion.span>
              {statusBadge === "working" && (
                <span className="worker-status-badge worker-status-working">Working</span>
              )}
              {statusBadge === "idle" && (
                <span className="worker-status-badge worker-status-idle">Idle</span>
              )}
              {(risk_ergo || risk_fatigue) && (
                <span className="worker-status-badge worker-status-at-risk">At risk</span>
              )}
              {isSample && (
                <span className="worker-status-badge worker-status-sample">Sample</span>
              )}
            </div>
          </div>
        </div>

        <div className="worker-card-risks">
          {risk_ergo && (
            <span className="risk-badge risk-ergo">Ergo</span>
          )}
          {risk_fatigue && (
            <span className="risk-badge risk-fatigue">Fatigue</span>
          )}
        </div>

        <div className="worker-card-updated">
          <User size={12} />
          <span>{isSample ? "Historical data" : `Updated ${formatUpdatedAt(updated_at)}`}</span>
        </div>

        {isSample && (
          <div className="worker-card-history">
            <button
              type="button"
              className="worker-card-history-toggle"
              onClick={() => setHistoryExpanded((e) => !e)}
              aria-expanded={historyExpanded}
            >
              <History size={14} />
              <span>{historyExpanded ? "Hide history" : "View history"}</span>
              <ChevronDown size={14} className={historyExpanded ? "worker-card-chevron-open" : ""} />
            </button>
            {historyExpanded && (
              <div className="worker-card-history-panel">
                {historyLoading ? (
                  <p className="worker-card-history-loading">Loading sessions…</p>
                ) : history.length === 0 ? (
                  <p className="worker-card-history-empty">No session history</p>
                ) : (
                  <ul className="worker-card-history-list">
                    {history.map((entry) => (
                      <li key={entry.session_id} className="worker-card-history-item">
                        <span className="worker-card-history-date">{formatSessionDate(entry.started_at)}</span>
                        <span className="worker-card-history-stats">
                          Active {entry.active_pct != null ? `${Math.round(entry.active_pct)}%` : "—"}
                          {" · "}
                          Idle {entry.idle_pct != null ? `${Math.round(entry.idle_pct)}%` : "—"}
                          {" · "}
                          Alerts {entry.alert_count}
                        </span>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </Card>
  );
}
