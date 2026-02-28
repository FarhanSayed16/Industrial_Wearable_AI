/**
 * Industrial Wearable AI — Privacy API Client
 */
import { apiClient } from "./client";

export interface ConsentRecord {
    status: "no_record" | "consented";
    consented_at?: string;
    retention_days?: string;
    opt_in_data_collection: boolean;
    opt_in_ai_analysis?: boolean;
}

export interface ConsentUpdate {
    retention_days: string;
    opt_in_data_collection: boolean;
    opt_in_ai_analysis: boolean;
}

export async function getWorkerConsent(workerId: string): Promise<ConsentRecord> {
    const { data } = await apiClient.get<ConsentRecord>(`/api/privacy/consent/${workerId}`);
    return data;
}

export async function updateWorkerConsent(workerId: string, payload: ConsentUpdate): Promise<void> {
    await apiClient.post(`/api/privacy/consent/${workerId}`, payload);
}

export async function purgeWorkerData(workerId: string): Promise<{ deleted_events: number; deleted_sessions: number }> {
    const { data } = await apiClient.delete(`/api/privacy/data/${workerId}`);
    return data;
}
