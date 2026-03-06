/**
 * Industrial Wearable AI — Shift Replay Page
 * Scrub through a past session and see worker state at each timestamp.
 */
import { useCallback, useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { apiClient } from "../api/client";
import { getActivityTimeline } from "../api/activity";
import "./ShiftReplay.css";

interface SessionDetail {
    id: string;
    worker_id: string;
    started_at: string;
    ended_at: string | null;
}

interface TimelineBucket {
    minute: string;
    sewing: number;
    adjusting: number;
    idle: number;
    break: number;
    error: number;
}

const STATE_COLORS: Record<string, string> = {
    sewing: "#22c55e",
    adjusting: "#3b82f6",
    idle: "#94a3b8",
    break: "#f59e0b",
    error: "#ef4444",
};

function dominantState(bucket: TimelineBucket): string {
    const states = ["sewing", "adjusting", "idle", "break", "error"] as const;
    let max = 0;
    let dominant = "idle";
    for (const s of states) {
        if (bucket[s] > max) {
            max = bucket[s];
            dominant = s;
        }
    }
    return dominant;
}

function formatTime(iso: string | null): string {
    if (!iso) return "—";
    return new Date(iso).toLocaleTimeString(undefined, { hour: "2-digit", minute: "2-digit" });
}

export default function ShiftReplay() {
    const { sessionId } = useParams<{ sessionId: string }>();
    const [session, setSession] = useState<SessionDetail | null>(null);
    const [timeline, setTimeline] = useState<TimelineBucket[]>([]);
    const [position, setPosition] = useState(0);
    const [playing, setPlaying] = useState(false);
    const [speed, setSpeed] = useState(1);
    const [loading, setLoading] = useState(true);

    const fetchData = useCallback(async () => {
        if (!sessionId) return;
        setLoading(true);
        try {
            // Get all sessions and find the matching one
            const res = await apiClient.get("/api/sessions");
            const sessions: SessionDetail[] = res.data;
            const found = sessions.find((s: SessionDetail) => s.id === sessionId);
            if (found) {
                setSession(found);
                const start = new Date(found.started_at).getTime();
                const end = found.ended_at ? new Date(found.ended_at).getTime() : Date.now();
                const data = await getActivityTimeline(start, end, 1);
                setTimeline(data);
            }
        } catch {
            // handled by interceptor
        } finally {
            setLoading(false);
        }
    }, [sessionId]);

    useEffect(() => {
        fetchData();
    }, [fetchData]);

    // Playback timer
    useEffect(() => {
        if (!playing || timeline.length === 0) return;
        const interval = setInterval(() => {
            setPosition((p) => {
                const next = p + 1;
                if (next >= timeline.length) {
                    setPlaying(false);
                    return timeline.length - 1;
                }
                return next;
            });
        }, 1000 / speed);
        return () => clearInterval(interval);
    }, [playing, speed, timeline.length]);

    const current = timeline[position] ?? null;
    const currentState = current ? dominantState(current) : "idle";

    if (loading) {
        return <div className="replay-loading">Loading replay…</div>;
    }

    if (!session) {
        return (
            <div className="replay-error">
                <p>Session not found.</p>
                <Link to="/sessions">← Back to Sessions</Link>
            </div>
        );
    }

    return (
        <div className="replay-page">
            <Link to="/sessions" className="replay-back">← Back to Sessions</Link>

            <div className="replay-header">
                <h1 className="replay-title">Shift Replay</h1>
                <span className="replay-session-info">
                    {formatTime(session.started_at)} — {formatTime(session.ended_at)}
                </span>
            </div>

            {/* State Display */}
            <div className="replay-state-card">
                <div
                    className="replay-state-indicator"
                    style={{ backgroundColor: STATE_COLORS[currentState] }}
                />
                <div className="replay-state-info">
                    <span className="replay-state-label">{currentState.toUpperCase()}</span>
                    <span className="replay-state-time">{current?.minute ?? "—"}</span>
                </div>
                {current && (
                    <div className="replay-state-counts">
                        {Object.entries(STATE_COLORS).map(([state, color]) => (
                            <span key={state} className="replay-count-chip" style={{ borderColor: color }}>
                                {state}: {current[state as keyof TimelineBucket]}
                            </span>
                        ))}
                    </div>
                )}
            </div>

            {/* Timeline Slider */}
            <div className="replay-controls">
                <button
                    className="replay-play-btn"
                    onClick={() => {
                        if (position >= timeline.length - 1) setPosition(0);
                        setPlaying(!playing);
                    }}
                >
                    {playing ? "⏸ Pause" : "▶ Play"}
                </button>
                <select
                    className="replay-speed-select"
                    value={speed}
                    onChange={(e) => setSpeed(Number(e.target.value))}
                >
                    <option value={1}>1×</option>
                    <option value={2}>2×</option>
                    <option value={5}>5×</option>
                    <option value={10}>10×</option>
                </select>
                <input
                    type="range"
                    className="replay-slider"
                    min={0}
                    max={Math.max(timeline.length - 1, 0)}
                    value={position}
                    onChange={(e) => {
                        setPosition(Number(e.target.value));
                        setPlaying(false);
                    }}
                />
                <span className="replay-position-label">
                    {position + 1} / {timeline.length}
                </span>
            </div>

            {/* Timeline Bar */}
            <div className="replay-timeline-bar">
                {timeline.map((b, i) => (
                    <div
                        key={i}
                        className={`replay-bar-segment ${i === position ? "replay-bar-segment--active" : ""}`}
                        style={{ backgroundColor: STATE_COLORS[dominantState(b)] }}
                        title={`${b.minute}: ${dominantState(b)}`}
                        onClick={() => { setPosition(i); setPlaying(false); }}
                    />
                ))}
            </div>
        </div>
    );
}
