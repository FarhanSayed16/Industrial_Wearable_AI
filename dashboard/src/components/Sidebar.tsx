/**
 * Industrial Wearable AI — Sidebar Navigation
 */
import { NavLink, useNavigate } from "react-router-dom";

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

const navItems = [
  { to: "/", label: "Live Overview" },
  { to: "/sessions", label: "Shift Summary" },
  { to: "/settings/password", label: "Change Password" },
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
        <div className="sidebar-header">
          <span className="sidebar-brand">Wearable AI</span>
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
