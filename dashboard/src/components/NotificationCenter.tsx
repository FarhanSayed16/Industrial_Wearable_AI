/**
 * Industrial Wearable AI — Notification Center Component
 * Displays a bell icon with unread count and a dropdown/popover 
 * of recent notifications.
 */
import { useEffect, useState, useRef, useCallback } from "react";
import { Bell, Check } from "lucide-react";
import { type Notification, notificationsApi } from "../api/notifications";
import "./NotificationCenter.css";

export default function NotificationCenter() {
    const [isOpen, setIsOpen] = useState(false);
    const [notifications, setNotifications] = useState<Notification[]>([]);
    const [unreadCount, setUnreadCount] = useState(0);
    const dropdownRef = useRef<HTMLDivElement>(null);

    const fetchNotifications = useCallback(async () => {
        try {
            const { data } = await notificationsApi.getNotifications(false);
            setNotifications(data);
            setUnreadCount(data.filter((n) => !n.read).length);
        } catch {
            // ignore
        }
    }, []);

    useEffect(() => {
        // eslint-disable-next-line
        fetchNotifications();
        const interval = setInterval(fetchNotifications, 60000); // Check every minute
        return () => clearInterval(interval);
    }, [fetchNotifications]);

    useEffect(() => {
        const handleClickOutside = (e: MouseEvent) => {
            if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
                setIsOpen(false);
            }
        };
        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    const handleMarkRead = async (id: string) => {
        try {
            await notificationsApi.markRead(id);
            setNotifications((prev) =>
                prev.map((n) => (n.id === id ? { ...n, read: true } : n))
            );
            setUnreadCount((c) => Math.max(0, c - 1));
        } catch { /* ignore */ }
    };

    const handleMarkAllRead = async () => {
        try {
            await notificationsApi.markAllRead();
            setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
            setUnreadCount(0);
        } catch { /* ignore */ }
    };

    return (
        <div className="nc-container" ref={dropdownRef}>
            <button
                className="nc-trigger"
                onClick={() => setIsOpen(!isOpen)}
                aria-label="Notifications"
            >
                <Bell size={20} />
                {unreadCount > 0 && <span className="nc-badge">{unreadCount}</span>}
            </button>

            {isOpen && (
                <div className="nc-dropdown">
                    <div className="nc-header">
                        <h4>Notifications</h4>
                        {unreadCount > 0 && (
                            <button className="nc-mark-all" onClick={handleMarkAllRead}>
                                <Check size={14} /> Mark all read
                            </button>
                        )}
                    </div>
                    <div className="nc-list">
                        {notifications.length === 0 ? (
                            <div className="nc-empty">No notifications</div>
                        ) : (
                            notifications.map((n) => (
                                <div key={n.id} className={`nc-item ${n.read ? "nc-read" : ""}`}>
                                    <div className={`nc-icon-badge nc-type-${n.type}`} />
                                    <div className="nc-content">
                                        <p className="nc-title">{n.title}</p>
                                        <p className="nc-body">{n.body}</p>
                                        <p className="nc-time">
                                            {new Date(n.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                        </p>
                                    </div>
                                    {!n.read && (
                                        <button
                                            className="nc-item-read-btn"
                                            onClick={() => handleMarkRead(n.id)}
                                            title="Mark as read"
                                        >
                                            <Check size={14} />
                                        </button>
                                    )}
                                </div>
                            ))
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}
