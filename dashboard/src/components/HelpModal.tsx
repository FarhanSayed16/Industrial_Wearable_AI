/**
 * Industrial Wearable AI — Help Modal (Keyboard Shortcuts)
 * Phase 5.2: ? to open, Esc to close
 */
import { useEffect } from "react";
import { createPortal } from "react-dom";
import { motion } from "framer-motion";
import { X } from "lucide-react";

interface HelpModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const shortcuts = [
  { key: "?", desc: "Show keyboard shortcuts" },
  { key: "Esc", desc: "Close modal or sidebar" },
];

export default function HelpModal({ isOpen, onClose }: HelpModalProps) {
  useEffect(() => {
    if (!isOpen) return;
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handleEsc);
    return () => window.removeEventListener("keydown", handleEsc);
  }, [isOpen, onClose]);

  useEffect(() => {
    if (isOpen) document.body.style.overflow = "hidden";
    return () => { document.body.style.overflow = ""; };
  }, [isOpen]);

  if (!isOpen) return null;

  return createPortal(
    <motion.div
      className="modal-overlay"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      onClick={onClose}
    >
      <motion.div
        className="help-modal"
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="help-modal-header">
          <h3>Keyboard Shortcuts</h3>
          <button
            type="button"
            className="help-modal-close"
            onClick={onClose}
            aria-label="Close"
          >
            <X size={20} />
          </button>
        </div>
        <ul className="help-modal-list">
          {shortcuts.map(({ key, desc }) => (
            <li key={key}>
              <kbd>{key}</kbd>
              <span>{desc}</span>
            </li>
          ))}
        </ul>
      </motion.div>
    </motion.div>,
    document.body
  );
}
