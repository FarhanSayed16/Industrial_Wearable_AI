/**
 * Industrial Wearable AI — Error State
 * Phase 4.6: Retry button, friendly copy
 */
import { motion } from "framer-motion";
import { AlertCircle, RefreshCw } from "lucide-react";

interface ErrorStateProps {
  message: string;
  onRetry?: () => void;
}

export default function ErrorState({ message, onRetry }: ErrorStateProps) {
  return (
    <motion.div
      className="error-state"
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <div className="error-state-icon">
        <AlertCircle size={40} />
      </div>
      <div className="error-state-title">Something went wrong</div>
      <p className="error-state-message">{message}</p>
      {onRetry && (
        <button
          type="button"
          className="error-state-retry"
          onClick={onRetry}
        >
          <RefreshCw size={16} />
          Try again
        </button>
      )}
    </motion.div>
  );
}
