/**
 * Industrial Wearable AI — Labeling Queue Page (Active Learning)
 * Review low-confidence predictions and provide human labels.
 */
import { useCallback, useEffect, useState } from "react";
import { apiClient } from "../api/client";
import "./LabelingQueue.css";

interface QueueItem {
    event_id: string;
    worker_name: string;
    timestamp: string;
    predicted_label: string;
    confidence: number;
}

const LABELS = ["sewing", "idle", "adjusting", "break", "error"];

const LABEL_COLORS: Record<string, string> = {
    sewing: "#22c55e",
    idle: "#94a3b8",
    adjusting: "#3b82f6",
    break: "#f59e0b",
    error: "#ef4444",
};

function formatTime(iso: string): string {
    if (!iso) return "—";
    const d = new Date(iso);
    return d.toLocaleString(undefined, {
        month: "short", day: "numeric", hour: "2-digit", minute: "2-digit",
    });
}

export default function LabelingQueue() {
    const [queue, setQueue] = useState<QueueItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [submitting, setSubmitting] = useState<Set<string>>(new Set());
    const [labeled, setLabeled] = useState<Set<string>>(new Set());

    const fetchQueue = useCallback(async () => {
        setLoading(true);
        try {
            const { data } = await apiClient.get<QueueItem[]>("/api/labels/queue", {
                params: { limit: 30 },
            });
            setQueue(data);
        } catch {
            // handled by interceptor
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchQueue();
    }, [fetchQueue]);

    const submitLabel = async (eventId: string, humanLabel: string) => {
        setSubmitting((prev) => new Set(prev).add(eventId));
        try {
            await apiClient.post("/api/labels", {
                event_id: eventId,
                human_label: humanLabel,
            });
            setLabeled((prev) => new Set(prev).add(eventId));
        } catch {
            // handled by interceptor
        } finally {
            setSubmitting((prev) => {
                const next = new Set(prev);
                next.delete(eventId);
                return next;
            });
        }
    };

    const pendingItems = queue.filter((q) => !labeled.has(q.event_id));
    const labeledCount = labeled.size;

    if (loading) {
        return <div className="lq-loading">Loading labeling queue…</div>;
    }

    return (
        <div className="lq-page">
            <div className="lq-header">
                <h1 className="lq-title">Labeling Queue</h1>
                <p className="lq-subtitle">
                    Review low-confidence predictions and correct them for model improvement.
                    {labeledCount > 0 && (
                        <span className="lq-labeled-count"> {labeledCount} labeled this session</span>
                    )}
                </p>
            </div>

            {pendingItems.length === 0 ? (
                <div className="lq-empty">
                    <span className="lq-empty-icon">✅</span>
                    <p>All events reviewed! No pending items in the queue.</p>
                </div>
            ) : (
                <div className="lq-list">
                    {pendingItems.map((item) => (
                        <div key={item.event_id} className="lq-card">
                            <div className="lq-card-header">
                                <span className="lq-worker">{item.worker_name}</span>
                                <span className="lq-time">{formatTime(item.timestamp)}</span>
                                <span
                                    className="lq-confidence"
                                    style={{
                                        color: item.confidence < 0.5 ? "#ef4444" : item.confidence < 0.7 ? "#f59e0b" : "#22c55e",
                                    }}
                                >
                                    {(item.confidence * 100).toFixed(0)}% confidence
                                </span>
                            </div>
                            <div className="lq-card-body">
                                <div className="lq-prediction">
                                    <span className="lq-pred-label">Model predicted:</span>
                                    <span
                                        className="lq-pred-badge"
                                        style={{ backgroundColor: LABEL_COLORS[item.predicted_label] || "#94a3b8" }}
                                    >
                                        {item.predicted_label}
                                    </span>
                                </div>
                                <div className="lq-actions">
                                    <span className="lq-action-label">Correct label:</span>
                                    {LABELS.map((label) => (
                                        <button
                                            key={label}
                                            className={`lq-label-btn ${label === item.predicted_label ? "lq-label-btn--predicted" : ""}`}
                                            style={{ borderColor: LABEL_COLORS[label] }}
                                            disabled={submitting.has(item.event_id)}
                                            onClick={() => submitLabel(item.event_id, label)}
                                        >
                                            {label}
                                        </button>
                                    ))}
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
