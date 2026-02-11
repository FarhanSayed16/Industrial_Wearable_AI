/**
 * Industrial Wearable AI — Sessions API
 */
import { apiClient } from "./client";

export interface Session {
  id: string;
  worker_id: string;
  worker_name: string | null;
  started_at: string;
  ended_at: string | null;
  shift_label: string | null;
}

export interface SessionSummary {
  session_id: string;
  worker_id: string;
  active_pct: number | null;
  idle_pct: number | null;
  adjusting_pct: number | null;
  error_pct: number | null;
  alert_count: number;
}

export async function getSessions(): Promise<Session[]> {
  const { data } = await apiClient.get<Session[]>("/api/sessions");
  return data;
}

export async function getSessionSummary(sessionId: string): Promise<SessionSummary> {
  const { data } = await apiClient.get<SessionSummary>(`/api/sessions/${sessionId}/summary`);
  return data;
}
