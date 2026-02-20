/**
 * Industrial Wearable AI — Alerts Trend (last 10 min)
 * Count of at-risk updates per minute.
 */
import { useMemo } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";
import type { ActivityEvent } from "../../hooks/useWebSocket";

const WINDOW_MS = 10 * 60 * 1000;

function bucketAlertsByMinute(events: ActivityEvent[]) {
  const now = Date.now();
  const cutoff = now - WINDOW_MS;
  const buckets: Record<number, number> = {};
  for (let t = Math.floor(cutoff / 60000) * 60000; t <= now; t += 60000) {
    buckets[t] = 0;
  }
  events.filter((e) => e.risk).forEach((e) => {
    if (e.ts < cutoff) return;
    const bucket = Math.floor(e.ts / 60000) * 60000;
    if (buckets[bucket] != null) buckets[bucket] += 1;
  });
  return Object.entries(buckets)
    .sort(([a], [b]) => Number(a) - Number(b))
    .map(([min, count]) => ({
      minute: new Date(Number(min)).toLocaleTimeString(undefined, { hour: "2-digit", minute: "2-digit" }),
      alerts: count,
    }));
}

export default function AlertsTrendChart({ events }: { events: ActivityEvent[] }) {
  const data = useMemo(() => bucketAlertsByMinute(events), [events]);

  return (
    <div className="alerts-trend-chart">
      <h4 className="chart-title" title="At-risk updates per minute">
        Alerts trend (last 10 min)
      </h4>
      <ResponsiveContainer width="100%" height={180}>
        <BarChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
          <XAxis dataKey="minute" tick={{ fontSize: 11 }} stroke="var(--color-text-muted)" />
          <YAxis tick={{ fontSize: 11 }} stroke="var(--color-text-muted)" allowDecimals={false} />
          <Tooltip
            contentStyle={{
              borderRadius: "var(--radius-md)",
              border: "1px solid var(--color-border)",
            }}
            formatter={(value: number | undefined) => [value ?? 0, "Alerts"]}
            labelFormatter={(label) => `Time: ${label}`}
          />
          <Bar dataKey="alerts" fill="var(--color-error)" radius={[4, 4, 0, 0]} name="Alerts" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
