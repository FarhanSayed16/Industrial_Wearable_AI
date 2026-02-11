/**
 * Industrial Wearable AI — Empty State
 * Phase 4.5: Icon + helpful message
 */
import { motion } from "framer-motion";

interface EmptyStateProps {
  icon?: React.ReactNode;
  title?: string;
  message: string;
}

export default function EmptyState({
  icon,
  title,
  message,
}: EmptyStateProps) {
  return (
    <motion.div
      className="empty-state"
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      {icon && <div className="empty-state-icon">{icon}</div>}
      {title && <div className="empty-state-title">{title}</div>}
      <p className="empty-state-message">{message}</p>
    </motion.div>
  );
}
