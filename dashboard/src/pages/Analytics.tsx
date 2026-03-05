/**
 * Industrial Wearable AI — Analytics Page
 * Rich analytics dashboard with productivity trends, heatmap, rankings, and state breakdown.
 */
import { useCallback, useEffect, useState } from "react";
import {
    LineChart, Line, BarChart, Bar, XAxis, YAxis, Tooltip,
    ResponsiveContainer, CartesianGrid, Legend, Cell,
} from "recharts";
import {
    getProductivity, getHeatmap, getRanking, getStateBreakdown, getInsights, getComplianceMetrics,
    type ProductivityPoint, type HeatmapRow, type RankingEntry, type StateBreakdownEntry, type Insight, type ComplianceMetrics
} from "../api/analytics";
import { AlertCircle, Search, Info, ShieldCheck } from "lucide-react";
import "./Analytics.css";

type DateRange = "7d" | "30d" | "90d";
const RANGE_MS: Record<DateRange, number> = {
    "7d": 7 * 86400000,
    "30d": 30 * 86400000,
    "90d": 90 * 86400000,
};
const RANGE_LABELS: { value: DateRange; label: string }[] = [
    { value: "7d", label: "Last 7 days" },
    { value: "30d", label: "Last 30 days" },
    { value: "90d", label: "Last 90 days" },
];

const STATE_COLORS: Record<string, string> = {
    sewing: "#22c55e",
    adjusting: "#3b82f6",
    idle: "#94a3b8",
    break: "#f59e0b",
    error: "#ef4444",
};

const WORKER_COLORS = [
    "#22c55e", "#3b82f6", "#f59e0b", "#ef4444", "#a855f7",
    "#ec4899", "#14b8a6", "#f97316",
];

function heatColor(value: number, max: number): string {
    if (max === 0) return "var(--color-bg)";
    const ratio = Math.min(value / max, 1);
    const h = 142 - ratio * 142; // green → red
    const s = 60 + ratio * 20;
    const l = 92 - ratio * 45;
    return `hsl(${h}, ${s}%, ${l}%)`;
}

export default function Analytics() {
    const [range, setRange] = useState<DateRange>("30d");
    const [productivity, setProductivity] = useState<ProductivityPoint[]>([]);
    const [heatmap, setHeatmap] = useState<HeatmapRow[]>([]);
    const [ranking, setRanking] = useState<RankingEntry[]>([]);
    const [breakdown, setBreakdown] = useState<StateBreakdownEntry[]>([]);
    const [insights, setInsights] = useState<Insight[]>([]);
    const [compliance, setCompliance] = useState<ComplianceMetrics | null>(null);
    const [loading, setLoading] = useState(true);

    const fetchAll = useCallback(async () => {
        setLoading(true);
        const now = Date.now();
        const from = now - RANGE_MS[range];
        try {
            const [p, h, r, b, i, c] = await Promise.all([
                getProductivity(from, now),
                getHeatmap(from, now),
                getRanking(from, now),
                getStateBreakdown(from, now),
                getInsights(parseInt(range.replace("d", ""), 10) || 7), // map "7d" to 7
                getComplianceMetrics(parseInt(range.replace("d", ""), 10) || 30) // map "30d" to 30
            ]);
            setProductivity(p);
            setHeatmap(h);
            setRanking(r);
            setBreakdown(b);
            setInsights(i);
            setCompliance(c);
        } catch {
            // errors handled by axios interceptor
        } finally {
            setLoading(false);
        }
    }, [range]);

    useEffect(() => {
        fetchAll();
    }, [fetchAll]);

    // Group productivity by day for multi-line chart
    const prodByDay = productivity.reduce<Record<string, Record<string, number>>>((acc, p) => {
        if (!acc[p.day]) acc[p.day] = {};
        acc[p.day][p.worker] = p.active_pct;
        return acc;
    }, {});
    const workerNames = [...new Set(productivity.map((p) => p.worker))];
    const prodChartData = Object.entries(prodByDay)
        .sort(([a], [b]) => a.localeCompare(b))
        .map(([day, workers]) => ({ day: day.slice(5), ...workers })); // "MM-DD"

    // Heatmap max for color scaling
    const heatMax = heatmap.reduce((m, row) =>
        Math.max(m, ...Object.values(row.hours)), 0);

    return (
        <div className="analytics-page">
            <div className="analytics-header">
                <h1 className="analytics-title">Analytics</h1>
                <select
                    className="analytics-range-select"
                    value={range}
                    onChange={(e) => setRange(e.target.value as DateRange)}
                    aria-label="Date range"
                >
                    {RANGE_LABELS.map((r) => (
                        <option key={r.value} value={r.value}>{r.label}</option>
                    ))}
                </select>
            </div>

            {loading ? (
                <div className="analytics-loading">Loading analytics…</div>
            ) : (
                <div className="analytics-grid">
                    {/* ── AI Insights ── */}
                    <section className="analytics-card analytics-card--wide" style={{ background: "linear-gradient(to right, #eff6ff, #f8fafc)", borderLeft: "4px solid #3b82f6" }}>
                        <h2 className="analytics-card-title" style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                            <Search size={18} color="#3b82f6" /> AI Root-Cause Insights
                        </h2>
                        <p className="analytics-card-subtitle">Automated causal analysis from recent sessions</p>
                        <ul style={{ listStyle: "none", padding: 0, margin: "1rem 0 0 0", display: "flex", flexDirection: "column", gap: "0.5rem" }}>
                            {insights.length === 0 ? (
                                <li style={{ color: "var(--color-text-muted)" }}>No notable insights for this period.</li>
                            ) : insights.map((insight, idx) => (
                                <li key={idx} style={{ padding: "1rem", background: "white", borderRadius: "8px", border: "1px solid #e2e8f0", display: "flex", gap: "1rem" }}>
                                    <div style={{ paddingTop: "0.2rem" }}>
                                        {insight.severity === "high" ? <AlertCircle size={20} color="#ef4444" /> :
                                            insight.severity === "medium" ? <AlertCircle size={20} color="#f59e0b" /> :
                                                <Info size={20} color="#10b981" />}
                                    </div>
                                    <div>
                                        <h4 style={{ margin: "0 0 0.25rem 0", fontSize: "0.95rem", color: "#1e293b" }}>{insight.title}</h4>
                                        <p style={{ margin: 0, fontSize: "0.85rem", color: "#475569", lineHeight: "1.4" }}>{insight.description}</p>
                                    </div>
                                </li>
                            ))}
                        </ul>
                    </section>

                    {/* ── ISO 45001 Compliance ── */}
                    {compliance && (
                        <section className="analytics-card" style={{ borderLeft: "4px solid #10b981" }}>
                            <h2 className="analytics-card-title" style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                                <ShieldCheck size={18} color="#10b981" /> ISO 45001 Compliance Metrics
                            </h2>
                            <p className="analytics-card-subtitle">Safety & Health Auditor Summary ({compliance.period_days} Days)</p>

                            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem", marginTop: "1rem" }}>
                                <div style={{ background: "#f8fafc", padding: "1rem", borderRadius: "8px", border: "1px solid #e2e8f0" }}>
                                    <p style={{ margin: 0, fontSize: "0.85rem", color: "#64748b" }}>Hours at Risk</p>
                                    <h3 style={{ margin: "0.25rem 0 0 0", color: "#1e293b", fontSize: "1.5rem" }}>{compliance.hours_at_risk}h</h3>
                                </div>
                                <div style={{ background: "#f8fafc", padding: "1rem", borderRadius: "8px", border: "1px solid #e2e8f0" }}>
                                    <p style={{ margin: 0, fontSize: "0.85rem", color: "#64748b" }}>Break Compliance</p>
                                    <h3 style={{ margin: "0.25rem 0 0 0", color: "#1e293b", fontSize: "1.5rem" }}>{compliance.break_compliance_pct}%</h3>
                                </div>
                                <div style={{ background: "#f8fafc", padding: "1rem", borderRadius: "8px", border: "1px solid #e2e8f0" }}>
                                    <p style={{ margin: 0, fontSize: "0.85rem", color: "#64748b" }}>Incident Rate</p>
                                    <h3 style={{ margin: "0.25rem 0 0 0", color: "#1e293b", fontSize: "1.5rem" }}>{compliance.incident_rate_per_100h} <span style={{ fontSize: "0.8rem", color: "#94a3b8" }}>/100h</span></h3>
                                </div>
                                <div style={{ background: "#f8fafc", padding: "1rem", borderRadius: "8px", border: "1px solid #e2e8f0" }}>
                                    <p style={{ margin: 0, fontSize: "0.85rem", color: "#64748b" }}>Highest Risk Profile</p>
                                    <h3 style={{ margin: "0.25rem 0 0 0", color: "#1e293b", fontSize: "1.1rem", textOverflow: "ellipsis", overflow: "hidden", whiteSpace: "nowrap" }} title={compliance.highest_risk_worker}>{compliance.highest_risk_worker}</h3>
                                </div>
                            </div>
                        </section>
                    )}

                    {/* ── Productivity Trend ── */}
                    <section className="analytics-card analytics-card--wide">
                        <h2 className="analytics-card-title">Productivity Trend</h2>
                        <p className="analytics-card-subtitle">Daily active % per worker</p>
                        {prodChartData.length === 0 ? (
                            <div className="analytics-empty">No productivity data for this period</div>
                        ) : (
                            <ResponsiveContainer width="100%" height={280}>
                                <LineChart data={prodChartData} margin={{ top: 8, right: 16, left: 0, bottom: 0 }}>
                                    <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                                    <XAxis dataKey="day" tick={{ fontSize: 11 }} stroke="var(--color-text-muted)" />
                                    <YAxis domain={[0, 100]} tick={{ fontSize: 11 }} stroke="var(--color-text-muted)" unit="%" />
                                    <Tooltip
                                        contentStyle={{
                                            background: "var(--color-bg-card)",
                                            border: "1px solid var(--color-border)",
                                            borderRadius: "var(--radius-md)",
                                        }}
                                        formatter={(v: number | undefined) => [`${v ?? 0}%`, ""]}
                                    />
                                    <Legend />
                                    {workerNames.map((w, i) => (
                                        <Line
                                            key={w}
                                            type="monotone"
                                            dataKey={w}
                                            stroke={WORKER_COLORS[i % WORKER_COLORS.length]}
                                            strokeWidth={2}
                                            dot={false}
                                            name={w}
                                        />
                                    ))}
                                </LineChart>
                            </ResponsiveContainer>
                        )}
                    </section>

                    {/* ── Worker Ranking ── */}
                    <section className="analytics-card">
                        <h2 className="analytics-card-title">Worker Ranking</h2>
                        <p className="analytics-card-subtitle">Average productivity score</p>
                        {ranking.length === 0 ? (
                            <div className="analytics-empty">No ranking data</div>
                        ) : (
                            <ResponsiveContainer width="100%" height={280}>
                                <BarChart data={ranking} layout="vertical" margin={{ top: 8, right: 16, left: 40, bottom: 0 }}>
                                    <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                                    <XAxis type="number" domain={[0, 100]} tick={{ fontSize: 11 }} stroke="var(--color-text-muted)" unit="%" />
                                    <YAxis type="category" dataKey="worker" tick={{ fontSize: 12 }} stroke="var(--color-text-muted)" width={50} />
                                    <Tooltip
                                        contentStyle={{
                                            background: "var(--color-bg-card)",
                                            border: "1px solid var(--color-border)",
                                            borderRadius: "var(--radius-md)",
                                        }}
                                        formatter={(v: number | undefined) => [`${v ?? 0}%`, "Active"]}
                                    />
                                    <Bar dataKey="avg_active_pct" name="Active %" radius={[0, 4, 4, 0]}>
                                        {ranking.map((_, i) => (
                                            <Cell key={i} fill={WORKER_COLORS[i % WORKER_COLORS.length]} />
                                        ))}
                                    </Bar>
                                </BarChart>
                            </ResponsiveContainer>
                        )}
                    </section>

                    {/* ── State Breakdown ── */}
                    <section className="analytics-card">
                        <h2 className="analytics-card-title">State Breakdown</h2>
                        <p className="analytics-card-subtitle">Activity distribution per worker</p>
                        {breakdown.length === 0 ? (
                            <div className="analytics-empty">No state data</div>
                        ) : (
                            <ResponsiveContainer width="100%" height={280}>
                                <BarChart data={breakdown} margin={{ top: 8, right: 16, left: 0, bottom: 0 }}>
                                    <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                                    <XAxis dataKey="worker" tick={{ fontSize: 11 }} stroke="var(--color-text-muted)" />
                                    <YAxis tick={{ fontSize: 11 }} stroke="var(--color-text-muted)" />
                                    <Tooltip
                                        contentStyle={{
                                            background: "var(--color-bg-card)",
                                            border: "1px solid var(--color-border)",
                                            borderRadius: "var(--radius-md)",
                                        }}
                                    />
                                    <Legend />
                                    {Object.entries(STATE_COLORS).map(([state, color]) => (
                                        <Bar key={state} dataKey={state} stackId="1" fill={color} name={state} />
                                    ))}
                                </BarChart>
                            </ResponsiveContainer>
                        )}
                    </section>

                    {/* ── Activity Heatmap ── */}
                    <section className="analytics-card analytics-card--wide">
                        <h2 className="analytics-card-title">Activity Heatmap</h2>
                        <p className="analytics-card-subtitle">Events per worker per hour of day</p>
                        {heatmap.length === 0 ? (
                            <div className="analytics-empty">No heatmap data</div>
                        ) : (
                            <div className="heatmap-container">
                                <div className="heatmap-header">
                                    <div className="heatmap-label" />
                                    {Array.from({ length: 24 }, (_, i) => (
                                        <div key={i} className="heatmap-hour-label">
                                            {i.toString().padStart(2, "0")}
                                        </div>
                                    ))}
                                </div>
                                {heatmap.map((row) => (
                                    <div key={row.worker} className="heatmap-row">
                                        <div className="heatmap-label">{row.worker}</div>
                                        {Array.from({ length: 24 }, (_, i) => (
                                            <div
                                                key={i}
                                                className="heatmap-cell"
                                                style={{ backgroundColor: heatColor(row.hours[i] || 0, heatMax) }}
                                                title={`${row.worker} @ ${i}:00 — ${row.hours[i] || 0} events`}
                                            />
                                        ))}
                                    </div>
                                ))}
                                <div className="heatmap-legend">
                                    <span>Low</span>
                                    <div className="heatmap-legend-bar" />
                                    <span>High</span>
                                </div>
                            </div>
                        )}
                    </section>
                </div>
            )}
        </div>
    );
}
