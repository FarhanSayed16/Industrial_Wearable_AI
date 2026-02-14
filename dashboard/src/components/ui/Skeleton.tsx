/**
 * Industrial Wearable AI — Skeleton loader
 */
interface SkeletonProps {
  width?: string | number;
  height?: string | number;
  borderRadius?: string | number;
  className?: string;
}

export default function Skeleton({
  width = "100%",
  height = 20,
  borderRadius = "var(--radius-md)",
  className = "",
}: SkeletonProps) {
  return (
    <div
      className={`skeleton ${className}`}
      style={{ width, height, borderRadius }}
    />
  );
}

export function SkeletonCard() {
  return (
    <div className="card skeleton-card">
      <Skeleton width="60%" height={20} className="skeleton-mb" />
      <Skeleton width="40%" height={24} className="skeleton-mb-sm" />
      <Skeleton width="80%" height={16} />
    </div>
  );
}
