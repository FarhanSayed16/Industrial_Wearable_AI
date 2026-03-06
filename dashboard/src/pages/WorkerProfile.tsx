/**
 * Industrial Wearable AI — Worker Profile Page
 * Detailed view for a single worker: info, session history, productivity chart.
 */
import { useCallback, useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import {
    LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid,
} from "recharts";
import { apiClient } from "../api/client";
import { getProductivity, type ProductivityPoint } from "../api/analytics";
import "./WorkerProfile.css";

interface WorkerInfo {
    id: string;
    name: string;
    role: string | null;
    created_at: string;
}

interface SessionEntry {
    session_id: string;
    started_at: string;
    ended_at: string | null;
    active_pct: number | null;
    idle_pct: number | null;
    adjusting_pct: number | null;
    error_pct: number | null;
    alert_count: number;
}

function formatDate(iso: string | null): string {
    if (!iso) return "—";
    const d = new Date(iso);
    return d.toLocaleDateString(undefined, { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" });
}

function pctBar(value: number | null, color: string) {
    const v = value ?? 0;
    return (
        <div className="wp-pct-bar">
            <div className="wp-pct-fill" style={{ width: `${v}%`, background: color }} />
            <span className="wp-pct-label">{v.toFixed(0)}%</span>
        </div>
    );
}

export default function WorkerProfile() {
    const { workerName } = useParams<{ workerName: string }>();
    const [worker, setWorker] = useState<WorkerInfo | null>(null);
    const [sessions, setSessions] = useState<SessionEntry[]>([]);
    const [trend, setTrend] = useState<ProductivityPoint[]>([]);
    const [loading, setLoading] = useState(true);

    const fetchData = useCallback(async () => {
        if (!workerName) return;
        setLoading(true);
        try {
            const [histRes, prodData] = await Promise.all([
                apiClient.get<SessionEntry[]>(`/api/workers/${workerName}/history`, { params: { limit: 30 } }),
                getProductivity(Date.now() - 30 * 86400000, Date.now(), workerName),
            ]);
            setSessions(histRes.data);
            setTrend(prodData);

            // Worker info from the workers list
            const wkRes = await apiClient.get<WorkerInfo[]>("/api/workers");
            const w = wkRes.data.find((w) => w.name === workerName);
            if (w) setWorker(w);
        } catch {
            // handled by interceptor
        } finally {
            setLoading(false);
        }
    }, [workerName]);

    useEffect(() => {
        fetchData();
    }, [fetchData]);

    const avgActive = sessions.length
        ? sessions.reduce((s, e) => s + (e.active_pct ?? 0), 0) / sessions.length
        : 0;
    const totalAlerts = sessions.reduce((s, e) => s + e.alert_count, 0);
    const totalSessions = sessions.length;

    const trendData = trend.map((p) => ({
        day: p.day.slice(5),
        active: p.active_pct,
    }));

    if (loading) {
        return <div className="wp-loading">Loading worker profile…</div>;
    }

    return (
        <div className="wp-page">
            <Link to="/" className="wp-back">← Back to Live View</Link>

            {/* Header Card */}
            <div className="wp-header-card">
                <div className="wp-avatar">{(workerName ?? "?")[0].toUpperCase()}</div>
                <div className="wp-header-info">
                    <h1 className="wp-name">{workerName}</h1>
                    <span className="wp-role">{worker?.role ?? "Sewing Operator"}</span>
                </div>
                <div className="wp-stats-row">
                    <div className="wp-stat">
                        <span className="wp-stat-value">{avgActive.toFixed(0)}%</span>
                        <span className="wp-stat-label">Avg Active</span>
                    </div>
                    <div className="wp-stat">
                        <span className="wp-stat-value">{totalAlerts}</span>
                        <span className="wp-stat-label">Alerts</span>
                    </div>
                    <div className="wp-stat">
                        <span className="wp-stat-value">{totalSessions}</span>
                        <span className="wp-stat-label">Sessions</span>
                    </div>
                </div>
            </div>

            {/* Productivity Trend */}
            <section className="wp-card">
                <h2 className="wp-card-title">Productivity Trend (30 days)</h2>
                {trendData.length === 0 ? (
                    <div className="wp-empty">No productivity data yet</div>
                ) : (
                    <ResponsiveContainer width="100%" height={220}>
                        <LineChart data={trendData} margin={{ top: 8, right: 16, left: 0, bottom: 0 }}>
                            <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                            <XAxis dataKey="day" tick={{ fontSize: 11 }} stroke="var(--color-text-muted)" />
                            <YAxis domain={[0, 100]} tick={{ fontSize: 11 }} stroke="var(--color-text-muted)" unit="%" />
                            <Tooltip
                                contentStyle={{
                                    background: "var(--color-bg-card)",
                                    border: "1px solid var(--color-border)",
                                    borderRadius: "var(--radius-md)",
                                }}
                                formatter={(v: number | undefined) => [`${v ?? 0}%`, "Active"]}
                            />
                            <Line type="monotone" dataKey="active" stroke="#22c55e" strokeWidth={2} dot={{ r: 3 }} />
                        </LineChart>
                    </ResponsiveContainer>
                )}
            </section>

            {/* Session History */}
            <section className="wp-card">
                <h2 className="wp-card-title">Session History</h2>
                {sessions.length === 0 ? (
                    <div className="wp-empty">No sessions recorded</div>
                ) : (
                    <div className="wp-table-wrap">
                        <table className="wp-table">
                            <thead>
                                <tr>
                                    <th>Date</th>
                                    <th>Active</th>
                                    <th>Idle</th>
                                    <th>Adjusting</th>
                                    <th>Alerts</th>
                                    <th></th>
                                </tr>
                            </thead>
                            <tbody>
                                {sessions.map((s) => (
                                    <tr key={s.session_id}>
                                        <td>{formatDate(s.started_at)}</td>
                                        <td>{pctBar(s.active_pct, "#22c55e")}</td>
                                        <td>{pctBar(s.idle_pct, "#94a3b8")}</td>
                                        <td>{pctBar(s.adjusting_pct, "#3b82f6")}</td>
                                        <td>
                                            <span className={`wp-alerts-badge ${s.alert_count > 0 ? "wp-alerts-badge--active" : ""}`}>
                                                {s.alert_count}
                                            </span>
                                        </td>
                                        <td>
                                            <Link to={`/replay/${s.session_id}`} className="wp-replay-link">Replay</Link>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </section>
        </div>
    );
}
