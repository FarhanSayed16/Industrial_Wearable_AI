/**
 * Industrial Wearable AI — Config API Client
 */
import { apiClient } from "./client";

export interface SystemConfigItem {
    key: string;
    value: string;
    description?: string;
}

export const configApi = {
    getAll: () => apiClient.get<SystemConfigItem[]>("/api/config"),

    setConfig: (item: SystemConfigItem) =>
        apiClient.post<SystemConfigItem>("/api/config", item),
};
