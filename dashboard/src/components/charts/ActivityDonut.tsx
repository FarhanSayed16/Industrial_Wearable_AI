/**
 * Industrial Wearable AI — Activity Donut Chart
 * Shows session breakdown: active, idle, adjusting, error
 */
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import type { SessionSummary } from "../../api/sessions";

const COLORS = ["#22c55e", "#94a3b8", "#3b82f6", "#ef4444"];

export default function ActivityDonut({ summary }: { summary: SessionSummary }) {
  const data = [
    { name: "Active (sewing)", value: summary.active_pct ?? 0, color: COLORS[0] },
    { name: "Idle", value: summary.idle_pct ?? 0, color: COLORS[1] },
    { name: "Adjusting", value: summary.adjusting_pct ?? 0, color: COLORS[2] },
    { name: "Error", value: summary.error_pct ?? 0, color: COLORS[3] },
  ].filter((d) => d.value > 0);

  if (data.length === 0) {
    return (
      <div className="chart-empty">
        No activity data for this session
      </div>
    );
  }

  return (
    <div className="activity-donut">
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
            formatter={(value: number | undefined) => (value != null ? `${value.toFixed(1)}%` : "")}
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
