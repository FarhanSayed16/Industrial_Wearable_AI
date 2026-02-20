/**
 * Industrial Wearable AI — Sessions / Shift Summary
 * Fetch sessions, select session, display aggregate summary.
 */
import { useCallback, useEffect, useState } from "react";
import { useLocation } from "react-router-dom";
import { Calendar, FileText } from "lucide-react";
import { getSessions, getSessionSummary, type Session, type SessionSummary } from "../api/sessions";
import ActivityDonut from "../components/charts/ActivityDonut";
import Card from "../components/ui/Card";
import EmptyState from "../components/EmptyState";
import ErrorState from "../components/ErrorState";
import Skeleton, { SkeletonCard } from "../components/ui/Skeleton";

function formatDate(iso: string) {
  try {
    return new Date(iso).toLocaleString();
  } catch {
    return iso;
  }
}

type DateFilter = "all" | "today" | "yesterday" | "7d" | "30d";

function filterSessionsByDate(sessions: Session[], filter: DateFilter): Session[] {
  if (filter === "all") return sessions;
  const now = new Date();
  const todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime();
  const dayMs = 24 * 60 * 60 * 1000;

  return sessions.filter((s) => {
    const t = new Date(s.started_at).getTime();
    switch (filter) {
      case "today":
        return t >= todayStart;
      case "yesterday":
        return t >= todayStart - dayMs && t < todayStart;
      case "7d":
        return t >= todayStart - 7 * dayMs;
      case "30d":
        return t >= todayStart - 30 * dayMs;
      default:
        return true;
    }
  });
}

function SummaryTable({ summary }: { summary: SessionSummary }) {
  const rows = [
    { label: "Active (sewing)", value: summary.active_pct, color: "#22c55e" },
    { label: "Idle", value: summary.idle_pct, color: "#94a3b8" },
    { label: "Adjusting", value: summary.adjusting_pct, color: "#3b82f6" },
    { label: "Error", value: summary.error_pct, color: "#ef4444" },
  ].filter((r) => r.value != null);

  return (
    <Card>
      <h3 style={{ margin: "0 0 1rem 0", fontSize: "1rem" }}>
        Worker: {summary.worker_id}
      </h3>
      <ActivityDonut summary={summary} />
      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          <tr style={{ borderBottom: "1px solid #e2e8f0" }}>
            <th style={{ textAlign: "left", padding: "0.5rem 0" }}>Activity</th>
            <th style={{ textAlign: "right", padding: "0.5rem 0" }}>%</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.label} style={{ borderBottom: "1px solid #f1f5f9" }}>
              <td style={{ padding: "0.5rem 0" }}>{r.label}</td>
              <td style={{ textAlign: "right", padding: "0.5rem 0", color: r.color }}>
                {r.value != null ? `${r.value.toFixed(1)}%` : "—"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {summary.alert_count > 0 && (
        <div
          style={{
            marginTop: "1rem",
            padding: "0.5rem",
            background: "#fef2f2",
            color: "#991b1b",
            borderRadius: 4,
            fontSize: "0.875rem",
          }}
        >
          Alerts during session: {summary.alert_count}
        </div>
      )}
    </Card>
  );
}

export default function Sessions() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [summary, setSummary] = useState<SessionSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dateFilter, setDateFilter] = useState<DateFilter>("all");

  const { pathname } = useLocation();

  const loadSessions = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getSessions();
      setSessions(data);
    } catch (e: unknown) {
      setError((e as Error)?.message ?? "Failed to load sessions");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadSessions();
  }, [loadSessions]);

  useEffect(() => {
    if (pathname !== "/sessions") return;
    const interval = setInterval(loadSessions, 30000);
    return () => clearInterval(interval);
  }, [pathname, loadSessions]);

  useEffect(() => {
    if (!selectedId) {
      setSummary(null);
      return;
    }
    let cancelled = false;
    (async () => {
      setSummary(null);
      try {
        const data = await getSessionSummary(selectedId);
        if (!cancelled) setSummary(data);
      } catch (e: unknown) {
        if (!cancelled) setError((e as Error)?.message ?? "Failed to load summary");
      }
    })();
    return () => { cancelled = true; };
  }, [selectedId]);

  if (loading) {
    return (
      <div className="sessions-loading">
        <div className="sessions-skeleton-list">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} width="100%" height={56} className="skeleton-mb" />
          ))}
        </div>
        <div className="sessions-skeleton-summary">
          <SkeletonCard />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <ErrorState message={error} onRetry={loadSessions} />
    );
  }

  const filteredSessions = filterSessionsByDate(sessions, dateFilter);

  return (
    <div className="sessions-grid">
      <div className="card sessions-list-card">
        <div className="sessions-list-header">
          <h3 style={{ margin: 0, fontSize: "0.875rem", color: "#64748b" }}>
            Sessions
          </h3>
          <select
            value={dateFilter}
            onChange={(e) => setDateFilter(e.target.value as DateFilter)}
            className="sessions-date-filter"
            aria-label="Filter by date"
          >
            <option value="all">All dates</option>
            <option value="today">Today</option>
            <option value="yesterday">Yesterday</option>
            <option value="7d">Last 7 days</option>
            <option value="30d">Last 30 days</option>
          </select>
        </div>
        {sessions.length === 0 ? (
          <EmptyState
            icon={<Calendar />}
            title="No sessions yet"
            message="Run the edge or simulator to create sessions."
          />
        ) : filteredSessions.length === 0 ? (
          <EmptyState
            icon={<Calendar />}
            title="No sessions in range"
            message="No sessions match the selected date filter."
          />
        ) : (
          <ul style={{ listStyle: "none", margin: 0, padding: 0 }}>
            {filteredSessions.map((s) => (
              <li key={s.id}>
                <button
                  type="button"
                  onClick={() => setSelectedId(s.id)}
                  style={{
                    width: "100%",
                    textAlign: "left",
                    padding: "0.75rem",
                    marginBottom: "0.25rem",
                    border: "1px solid #e2e8f0",
                    borderRadius: 6,
                    background: selectedId === s.id ? "#eff6ff" : "#fff",
                    cursor: "pointer",
                    fontSize: "0.875rem",
                  }}
                >
                  <div style={{ fontWeight: 600 }}>
                    {s.worker_name ?? s.worker_id ?? "Unknown"}
                  </div>
                  <div style={{ color: "#64748b", fontSize: "0.75rem" }}>
                    {formatDate(s.started_at)}
                  </div>
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>

      <div>
        {selectedId && summary ? (
          <SummaryTable summary={summary} />
        ) : selectedId ? (
          <div style={{ padding: "2rem", color: "#64748b" }}>
            Loading summary...
          </div>
        ) : (
          <EmptyState
            icon={<FileText />}
            title="Select a session"
            message="Choose a session from the list to view its activity summary."
          />
        )}
      </div>
    </div>
  );
}
