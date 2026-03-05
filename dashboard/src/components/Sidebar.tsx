/**
 * Industrial Wearable AI — Sidebar Navigation
 */
import { NavLink, useNavigate } from "react-router-dom";
import NotificationCenter from "./NotificationCenter";

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

const navItems = [
  { to: "/", label: "Live Overview" },
  { to: "/map", label: "Floor Map" },
  { to: "/sessions", label: "Shift Summary" },
  { to: "/analytics", label: "Analytics" },
  { to: "/labeling", label: "Labeling Queue" },
  { to: "/privacy", label: "Privacy & Consent" },
  { to: "/settings", label: "Settings" },
];

export default function Sidebar({ isOpen, onClose }: SidebarProps) {
  const navigate = useNavigate();

  const handleLogout = () => {
    if (!window.confirm("Are you sure you want to log out?")) return;
    localStorage.removeItem("access_token");
    localStorage.removeItem("remember_me");
    navigate("/login", { replace: true });
  };

  return (
    <>
      <aside className={`sidebar ${isOpen ? "sidebar-open" : ""}`}>
        <div className="sidebar-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%', paddingRight: '1rem' }}>
          <span className="sidebar-brand">Wearable AI</span>
          <NotificationCenter />
        </div>
        <nav className="sidebar-nav">
          {navItems.map(({ to, label }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `sidebar-link ${isActive ? "sidebar-link-active" : ""}`
              }
              onClick={onClose}
              end={to === "/"}
            >
              {label}
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-footer">
          <button
            type="button"
            className="sidebar-link sidebar-logout"
            onClick={handleLogout}
          >
            Logout
          </button>
        </div>
      </aside>
      <div
        className="sidebar-overlay"
        aria-hidden={!isOpen}
        onClick={onClose}
      />
    </>
  );
}
