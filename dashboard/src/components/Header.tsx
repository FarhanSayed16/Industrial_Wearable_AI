/**
 * Industrial Wearable AI — Header with page title and connection status
 */
import { useAuth } from "../hooks/useAuth";
import { useWebSocket } from "../hooks/useWebSocket";

interface HeaderProps {
  title: string;
}

export default function Header({ title }: HeaderProps) {
  const { connected } = useWebSocket();
  const { user } = useAuth();

  return (
    <header className="app-header">
      <h1 className="app-header-title">{title}</h1>
      <div className="app-header-actions">
        <span
          className={`connection-badge ${connected ? "connection-badge-online" : "connection-badge-offline"}`}
          title={connected ? "WebSocket connected" : "WebSocket disconnected"}
        >
          <span className="connection-dot" />
          {connected ? "Connected" : "Disconnected"}
        </span>
        <span className="app-header-user">{user?.username ?? "—"}</span>
      </div>
    </header>
  );
}
