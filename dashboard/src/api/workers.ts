/**
 * Industrial Wearable AI — Workers API
 */
import { apiClient } from "./client";

export interface WorkerOut {
  id: string;
  name: string;
  role: string | null;
  device_id: string | null;
  created_at: string;
}

export interface WorkerHistoryEntry {
  session_id: string;
  started_at: string;
  ended_at: string | null;
  active_pct: number | null;
  idle_pct: number | null;
  adjusting_pct: number | null;
  error_pct: number | null;
  alert_count: number;
}

export async function getWorkers(): Promise<WorkerOut[]> {
  const { data } = await apiClient.get<WorkerOut[]>("/api/workers");
  return data ?? [];
}

export async function getWorkerHistory(workerName: string, limit?: number): Promise<WorkerHistoryEntry[]> {
  const params = limit != null ? { limit } : undefined;
  const { data } = await apiClient.get<WorkerHistoryEntry[]>(`/api/workers/${encodeURIComponent(workerName)}/history`, { params });
  return data ?? [];
}
