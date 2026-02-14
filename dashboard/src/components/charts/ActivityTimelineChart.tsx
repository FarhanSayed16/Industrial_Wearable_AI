/**
 * Industrial Wearable AI — Activity Timeline
 * Live (10 min) or historical (1h, 6h, 24h) with time range selector.
 */
import { useEffect, useMemo, useState } from "react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";
import { getActivityTimeline } from "../../api/activity";
import type { ActivityEvent } from "../../hooks/useWebSocket";

const WINDOW_MS_10M = 10 * 60 * 1000;
const STATE_ORDER = ["sewing", "adjusting", "idle", "break", "error"];
const STATE_COLORS: Record<string, string> = {
  sewing: "#22c55e",
  adjusting: "#3b82f6",
  idle: "#94a3b8",
  break: "#f59e0b",
  error: "#ef4444",
};

export type TimelineRange = "10m" | "1h" | "6h" | "24h";

const RANGE_OPTIONS: { value: TimelineRange; label: string }[] = [
  { value: "10m", label: "Last 10 min (live)" },
  { value: "1h", label: "Last 1 hour" },
  { value: "6h", label: "Last 6 hours" },
  { value: "24h", label: "Last 24 hours" },
];

function bucketByMinute(events: ActivityEvent[], windowMs: number) {
  const now = Date.now();
  const cutoff = now - windowMs;
  const buckets: Record<number, Record<string, number>> = {};
  for (let t = Math.floor(cutoff / 60000) * 60000; t <= now; t += 60000) {
    buckets[t] = { sewing: 0, adjusting: 0, idle: 0, break: 0, error: 0 };
  }
  events.forEach((e) => {
    if (e.ts < cutoff) return;
    const bucket = Math.floor(e.ts / 60000) * 60000;
    if (!buckets[bucket]) buckets[bucket] = { sewing: 0, adjusting: 0, idle: 0, break: 0, error: 0 };
    const s = STATE_ORDER.includes(e.label) ? e.label : "idle";
    buckets[bucket][s] = (buckets[bucket][s] ?? 0) + 1;
  });
  return Object.entries(buckets)
    .sort(([a], [b]) => Number(a) - Number(b))
    .map(([min, counts]) => ({
      minute: new Date(Number(min)).toLocaleTimeString(undefined, { hour: "2-digit", minute: "2-digit" }),
      ...counts,
    }));
}

export default function ActivityTimelineChart({ events }: { events: ActivityEvent[] }) {
  const [timeRange, setTimeRange] = useState<TimelineRange>("10m");
  const [historicalData, setHistoricalData] = useState<{ minute: string; sewing: number; adjusting: number; idle: number; break: number; error: number }[] | null>(null);
  const [historicalLoading, setHistoricalLoading] = useState(false);

  const liveData = useMemo(() => bucketByMinute(events, WINDOW_MS_10M), [events]);

  useEffect(() => {
    if (timeRange === "10m") {
      setHistoricalData(null);
      return;
    }
    const now = Date.now();
    const ms = timeRange === "1h" ? 60 * 60 * 1000 : timeRange === "6h" ? 6 * 60 * 60 * 1000 : 24 * 60 * 60 * 1000;
    const fromTs = now - ms;
    const bucketMinutes = timeRange === "1h" ? 1 : timeRange === "6h" ? 5 : 15;
    setHistoricalLoading(true);
    getActivityTimeline(fromTs, now, bucketMinutes)
      .then((data) => setHistoricalData(data))
      .catch(() => setHistoricalData([]))
      .finally(() => setHistoricalLoading(false));
  }, [timeRange]);

  const data = timeRange === "10m" ? liveData : historicalData ?? [];
  const isEmpty = data.length === 0 && !historicalLoading;

  return (
    <div className="activity-timeline-chart">
      <div className="chart-header-with-controls">
        <h4 className="chart-title" title="Activity by state over time">
          Activity timeline
        </h4>
        <select
          className="chart-time-range-select"
          value={timeRange}
          onChange={(e) => setTimeRange(e.target.value as TimelineRange)}
          aria-label="Time range"
        >
          {RANGE_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </div>
      {historicalLoading ? (
        <div className="chart-empty">Loading timeline…</div>
      ) : isEmpty ? (
        <div className="chart-empty">
          {timeRange === "10m"
            ? "Activity will appear as updates are received (last 10 min)"
            : "No activity data for this period"}
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={220}>
          <AreaChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
            <XAxis dataKey="minute" tick={{ fontSize: 11 }} stroke="var(--color-text-muted)" />
            <YAxis tick={{ fontSize: 11 }} stroke="var(--color-text-muted)" allowDecimals={false} />
            <Tooltip
              contentStyle={{
                borderRadius: "var(--radius-md)",
                border: "1px solid var(--color-border)",
              }}
              formatter={(value: number) => [value, ""]}
              labelFormatter={(label) => `Time: ${label}`}
            />
            {STATE_ORDER.map((state) => (
              <Area
                key={state}
                type="monotone"
                dataKey={state}
                stackId="1"
                stroke={STATE_COLORS[state]}
                fill={STATE_COLORS[state]}
                fillOpacity={0.7}
                name={state}
              />
            ))}
          </AreaChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
