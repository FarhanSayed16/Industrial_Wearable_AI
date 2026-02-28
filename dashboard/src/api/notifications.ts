/**
 * Industrial Wearable AI — Notification Center API Client
 */
import { apiClient } from "./client";

export interface Notification {
    id: string;
    type: string;
    title: string;
    body: string;
    read: boolean;
    created_at: string;
}

export const notificationsApi = {
    getNotifications: (unreadOnly = false) =>
        apiClient.get<Notification[]>("/api/notifications", { params: { unread_only: unreadOnly } }),

    markRead: (id: string) =>
        apiClient.put(`/api/notifications/${id}/read`),

    markAllRead: () =>
        apiClient.post("/api/notifications/mark-all-read"),
};
