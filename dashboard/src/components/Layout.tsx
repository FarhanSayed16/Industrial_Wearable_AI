/**
 * Industrial Wearable AI — App Shell with Sidebar and Header
 */
import { useEffect, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Outlet, useLocation } from "react-router-dom";
import "./Layout.css";
import Header from "./Header";
import HelpModal from "./HelpModal";
import Sidebar from "./Sidebar";

const PAGE_TITLES: Record<string, string> = {
  "/": "Live Overview",
  "/sessions": "Shift Summary",
  "/settings/password": "Change Password",
};

function getPageTitle(pathname: string): string {
  return PAGE_TITLES[pathname] ?? "Dashboard";
}

export default function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [helpOpen, setHelpOpen] = useState(false);
  const { pathname } = useLocation();
  const title = getPageTitle(pathname);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      const target = e.target as HTMLElement;
      const isInput = /^(INPUT|TEXTAREA|SELECT)$/.test(target.tagName) || target.isContentEditable;

      if (e.key === "?" && !isInput) {
        e.preventDefault();
        setHelpOpen((o) => !o);
      }
      if (e.key === "Escape") {
        setHelpOpen(false);
        setSidebarOpen(false);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  return (
    <div className="app-shell">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      <HelpModal isOpen={helpOpen} onClose={() => setHelpOpen(false)} />
      <div className="app-main">
        <button
          type="button"
          className="sidebar-toggle"
          onClick={() => setSidebarOpen(true)}
          aria-label="Open menu"
        >
          <span className="sidebar-toggle-bar" />
          <span className="sidebar-toggle-bar" />
          <span className="sidebar-toggle-bar" />
        </button>
        <Header title={title} />
        <main className="app-content">
          <AnimatePresence mode="wait">
            <motion.div
              key={pathname}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.2 }}
            >
              <Outlet />
            </motion.div>
          </AnimatePresence>
        </main>
      </div>
    </div>
  );
}
