/**
 * Industrial Wearable AI — Analytics API client
 */
import { apiClient } from "./client";

export interface ProductivityPoint {
    worker: string;
    day: string;
    active_pct: number;
}

export interface HeatmapRow {
    worker: string;
    hours: Record<number, number>;
}

export interface RankingEntry {
    worker: string;
    avg_active_pct: number;
    avg_idle_pct: number;
    total_alerts: number;
    session_count: number;
}

export interface StateBreakdownEntry {
    worker: string;
    sewing: number;
    idle: number;
    adjusting: number;
    break: number;
    error: number;
}

export async function getProductivity(fromTs?: number, toTs?: number, workerName?: string) {
    const { data } = await apiClient.get<ProductivityPoint[]>("/api/analytics/productivity", {
        params: { from_ts: fromTs, to_ts: toTs, worker_name: workerName },
    });
    return data;
}

export async function getHeatmap(fromTs?: number, toTs?: number) {
    const { data } = await apiClient.get<HeatmapRow[]>("/api/analytics/heatmap", {
        params: { from_ts: fromTs, to_ts: toTs },
    });
    return data;
}

export async function getRanking(fromTs?: number, toTs?: number) {
    const { data } = await apiClient.get<RankingEntry[]>("/api/analytics/ranking", {
        params: { from_ts: fromTs, to_ts: toTs },
    });
    return data;
}

export async function getStateBreakdown(fromTs?: number, toTs?: number) {
    const { data } = await apiClient.get<StateBreakdownEntry[]>("/api/analytics/state-breakdown", {
        params: { from_ts: fromTs, to_ts: toTs },
    });
    return data;
}

export interface Insight {
    type: string;
    severity: string;
    title: string;
    description: string;
}

export async function getInsights(days: number = 7) {
    const { data } = await apiClient.get<Insight[]>("/api/analytics/insights", {
        params: { days },
    });
    return data;
}

export interface ComplianceMetrics {
    period_days: number;
    hours_at_risk: number;
    break_compliance_pct: number;
    incident_rate_per_100h: number;
    total_hours_worked: number;
    highest_risk_worker: string;
}

export async function getComplianceMetrics(days: number = 30) {
    const { data } = await apiClient.get<ComplianceMetrics>("/api/compliance/metrics", {
        params: { days }
    });
    return data;
}
