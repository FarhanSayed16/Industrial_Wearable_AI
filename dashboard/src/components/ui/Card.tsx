/**
 * Industrial Wearable AI — Card component
 * Soft shadow, hover lift, theme-aware
 */
import { motion } from "framer-motion";

interface CardProps {
  children: React.ReactNode;
  className?: string;
}

export default function Card({ children, className = "" }: CardProps) {
  return (
    <motion.div
      className={`card ${className}`}
      whileHover={{ y: -2, boxShadow: "0 8px 25px -5px rgba(0,0,0,0.1), 0 4px 10px -6px rgba(0,0,0,0.1)" }}
      transition={{ duration: 0.2 }}
    >
      {children}
    </motion.div>
  );
}
