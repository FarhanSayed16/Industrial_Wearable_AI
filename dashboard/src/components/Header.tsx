/**
 * Industrial Wearable AI — Header with page title and connection status
 */
import { useAuth } from "../hooks/useAuth";
import { useWebSocket } from "../hooks/useWebSocket";
import { ConnectionStatus } from "./ConnectionStatus";

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
        <ConnectionStatus status={connected ? "connected" : "disconnected"} />
        <span className="app-header-user">{user?.username ?? "—"}</span>
      </div>
    </header>
  );
}
