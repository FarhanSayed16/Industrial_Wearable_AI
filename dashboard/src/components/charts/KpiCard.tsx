/**
 * Industrial Wearable AI — KPI Card
 * Small stat card for Live View
 */
import { motion } from "framer-motion";

interface KpiCardProps {
  label: string;
  value: number;
  color?: string;
  /** Tooltip (e.g. "Working = currently sewing") */
  title?: string;
}

type ColorKey = "primary" | "success" | "idle" | "error" | "muted";

export default function KpiCard({ label, value, color, title }: KpiCardProps) {
  const colorKey: ColorKey | undefined =
    color === "var(--color-success)" || color?.includes("success") ? "success" :
    color === "var(--color-idle)" || color?.includes("idle") ? "idle" :
    color === "var(--color-error)" || color?.includes("error") ? "error" :
    color === "var(--color-text-muted)" || label === "Sample" ? "muted" :
    "primary";
  return (
    <motion.div
      className="kpi-card"
      data-color={colorKey}
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.2 }}
      title={title}
    >
      <span className="kpi-value" style={color ? { color } : undefined}>
        {value}
      </span>
      <span className="kpi-label">{label}</span>
    </motion.div>
  );
}
