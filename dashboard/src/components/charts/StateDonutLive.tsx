/**
 * Industrial Wearable AI — Live State Distribution Donut
 * Shows current worker counts by state (sewing, idle, adjusting, error, break).
 */
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import type { WorkerState } from "../../hooks/useWebSocket";

const STATE_COLORS: Record<string, string> = {
  sewing: "#22c55e",
  idle: "#94a3b8",
  adjusting: "#3b82f6",
  error: "#ef4444",
  break: "#f59e0b",
};

const STATE_LABELS: Record<string, string> = {
  sewing: "Sewing",
  idle: "Idle",
  adjusting: "Adjusting",
  error: "Error",
  break: "Break",
};

export default function StateDonutLive({ workers }: { workers: WorkerState[] }) {
  const data = Object.entries(
    workers.reduce<Record<string, number>>((acc, w) => {
      const s = w.current_state || "idle";
      acc[s] = (acc[s] ?? 0) + 1;
      return acc;
    }, {})
  )
    .map(([state, count]) => ({
      name: STATE_LABELS[state] ?? state,
      value: count,
      color: STATE_COLORS[state] ?? "#94a3b8",
    }))
    .filter((d) => d.value > 0);

  if (data.length === 0) {
    return (
      <div className="chart-empty">
        No workers — state distribution will appear when data is received
      </div>
    );
  }

  return (
    <div className="activity-donut state-donut-live">
      <h4 className="chart-title" title="Current count of workers in each activity state">
        State distribution (now)
      </h4>
      <ResponsiveContainer width="100%" height={220}>
        <PieChart>
          <Pie
            data={data}
            dataKey="value"
            nameKey="name"
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={90}
            paddingAngle={2}
            isAnimationActive
            animationDuration={600}
          >
            {data.map((entry) => (
              <Cell key={entry.name} fill={entry.color} />
            ))}
          </Pie>
          <Tooltip
            formatter={(value: number | undefined) => (value != null ? `${value} worker(s)` : "")}
            contentStyle={{
              borderRadius: "var(--radius-md)",
              border: "1px solid var(--color-border)",
            }}
          />
          <Legend
            verticalAlign="bottom"
            height={36}
            formatter={(value) => value}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
