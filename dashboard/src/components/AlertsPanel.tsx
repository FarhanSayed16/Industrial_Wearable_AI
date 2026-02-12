/**
 * Industrial Wearable AI — Alerts Panel
 * Phase 4.3: Animated list, severity indicator, expand/collapse
 */
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { AlertTriangle, ChevronDown, ChevronUp } from "lucide-react";
import type { WorkerState } from "../hooks/useWebSocket";

interface AlertsPanelProps {
  workers: WorkerState[];
}

type Severity = "high" | "medium";

function getSeverity(w: WorkerState): Severity {
  if (w.risk_ergo && w.risk_fatigue) return "high";
  return "medium";
}

export default function AlertsPanel({ workers }: AlertsPanelProps) {
  const [expanded, setExpanded] = useState(true);
  const alerts = workers.filter((w) => w.risk_ergo || w.risk_fatigue);

  if (alerts.length === 0) {
    return (
      <motion.div
        className="alerts-panel alerts-panel-ok"
        initial={{ opacity: 0, y: -8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.2 }}
      >
        <strong>No active alerts</strong>
        <span>All workers within safe parameters</span>
      </motion.div>
    );
  }

  return (
    <motion.div
      className="alerts-panel alerts-panel-active"
      initial={{ opacity: 0, y: -8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
    >
      <button
        type="button"
        className="alerts-panel-header"
        onClick={() => setExpanded(!expanded)}
        aria-expanded={expanded}
      >
        <AlertTriangle size={18} />
        <strong>Active Alerts ({alerts.length})</strong>
        {expanded ? (
          <ChevronUp size={18} className="alerts-chevron" />
        ) : (
          <ChevronDown size={18} className="alerts-chevron" />
        )}
      </button>

      <AnimatePresence>
        {expanded && (
          <motion.ul
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="alerts-list"
          >
            {alerts.map((w, i) => {
              const severity = getSeverity(w);
              const reasons = [w.risk_ergo && "Ergonomics", w.risk_fatigue && "Fatigue"]
                .filter(Boolean)
                .join(", ");
              const updatedAgo = w.updated_at
                ? (() => {
                    const sec = (Date.now() - w.updated_at) / 1000;
                    if (sec < 60) return "just now";
                    if (sec < 3600) return `${Math.floor(sec / 60)}m ago`;
                    return new Date(w.updated_at).toLocaleTimeString();
                  })()
                : null;
              return (
                <motion.li
                  key={w.worker_id}
                  initial={{ opacity: 0, x: -8 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.05, duration: 0.2 }}
                  className={`alerts-item alerts-severity-${severity}`}
                >
                  <span className="alerts-severity-dot" data-severity={severity} />
                  <strong>{w.name}</strong>
                  <span>{reasons}</span>
                  {updatedAgo && (
                    <span className="alerts-item-updated" title="Last updated">
                      Updated {updatedAgo}
                    </span>
                  )}
                </motion.li>
              );
            })}
          </motion.ul>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
