/**
 * Industrial Wearable AI — Filters
 * Phase 4.4: Pill buttons, clear filters
 */
import { X } from "lucide-react";

const STATE_OPTIONS = [
  { value: "all" as const, label: "All states" },
  { value: "idle" as const, label: "Idle" },
  { value: "sewing" as const, label: "Sewing" },
  { value: "adjusting" as const, label: "Adjusting" },
  { value: "error" as const, label: "Error" },
];

const RISK_OPTIONS = [
  { value: "all" as const, label: "All" },
  { value: "at_risk" as const, label: "At risk" },
  { value: "ok" as const, label: "OK" },
];

interface FiltersProps {
  stateFilter: "all" | "idle" | "sewing" | "adjusting" | "error";
  riskFilter: "all" | "at_risk" | "ok";
  onStateChange: (v: typeof STATE_OPTIONS[number]["value"]) => void;
  onRiskChange: (v: typeof RISK_OPTIONS[number]["value"]) => void;
}

export default function Filters({
  stateFilter,
  riskFilter,
  onStateChange,
  onRiskChange,
}: FiltersProps) {
  const hasFilters = stateFilter !== "all" || riskFilter !== "all";

  const clearFilters = () => {
    onStateChange("all");
    onRiskChange("all");
  };

  return (
    <div className="filters-row">
      <span className="filters-label">State:</span>
      <div className="filter-pills">
        {STATE_OPTIONS.map((opt) => (
          <button
            key={opt.value}
            type="button"
            className={`filter-pill ${stateFilter === opt.value ? "filter-pill-active" : ""}`}
            onClick={() => onStateChange(opt.value)}
          >
            {opt.label}
          </button>
        ))}
      </div>
      <span className="filters-label">Risk:</span>
      <div className="filter-pills">
        {RISK_OPTIONS.map((opt) => (
          <button
            key={opt.value}
            type="button"
            className={`filter-pill ${riskFilter === opt.value ? "filter-pill-active" : ""}`}
            onClick={() => onRiskChange(opt.value)}
          >
            {opt.label}
          </button>
        ))}
      </div>
      {hasFilters && (
        <button
          type="button"
          className="filter-clear"
          onClick={clearFilters}
          title="Clear filters"
        >
          <X size={14} />
          Clear
        </button>
      )}
    </div>
  );
}
