/**
 * Industrial Wearable AI — WebSocket Hook
 * Connects to VITE_WS_URL, receives live state, returns worker map.
 * Auto-reconnects on disconnect with exponential backoff.
 * Buffers last 10 min of updates for activity timeline and alerts trend.
 */
import { useCallback, useEffect, useRef, useState } from "react";

export interface WorkerState {
  worker_id: string;
  name: string;
  current_state: string;
  risk_ergo: boolean;
  risk_fatigue: boolean;
  updated_at: number;
}

export interface ActivityEvent {
  ts: number;
  worker_id: string;
  label: string;
  risk: boolean;
}

export interface SensorSnapshot {
  temp?: number;
  accel_mag?: number;
  ts: number;
}

const TIMELINE_WINDOW_MS = 10 * 60 * 1000; // 10 min
const MAX_TIMELINE_EVENTS = 2000;

function getWsUrl(): string {
  const env = import.meta.env.VITE_WS_URL;
  if (env && typeof env === "string" && env.startsWith("ws") && !env.includes("<URL")) {
    return env;
  }
  const api = import.meta.env.VITE_API_URL;
  if (api && typeof api === "string") {
    const base = api.replace(/^http/, "ws");
    return `${base.replace(/\/$/, "")}/ws/live`;
  }
  return "ws://localhost:8000/ws/live";
}
const wsUrl = getWsUrl();
const MAX_RECONNECT_DELAY = 30000;
const INITIAL_RECONNECT_DELAY = 1000;

export function useWebSocket() {
  const [workers, setWorkers] = useState<Record<string, WorkerState>>({});
  const [sensorByWorker, setSensorByWorker] = useState<Record<string, SensorSnapshot>>({});
  const [mpuConnectedByWorker, setMpuConnectedByWorker] = useState<Record<string, boolean>>({});
  const [connected, setConnected] = useState(false);
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const reconnectDelayRef = useRef(INITIAL_RECONNECT_DELAY);
  const timelineRef = useRef<ActivityEvent[]>([]);

  useEffect(() => {
    let ws: WebSocket | null = null;
    let mounted = true;

    function connect() {
      if (!mounted) return;
      ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        if (mounted) {
          setConnected(true);
          reconnectDelayRef.current = INITIAL_RECONNECT_DELAY;
        }
      };

      ws.onclose = () => {
        if (mounted) setConnected(false);
        if (!mounted) return;
        reconnectTimeoutRef.current = setTimeout(() => {
          connect();
          reconnectDelayRef.current = Math.min(
            reconnectDelayRef.current * 2,
            MAX_RECONNECT_DELAY
          );
        }, reconnectDelayRef.current);
      };

      ws.onerror = () => {
        if (mounted) setConnected(false);
      };

      ws.onmessage = (event) => {
        try {
          const raw = JSON.parse(event.data) as Record<string, unknown>;
          if (raw.type === "sensor" && typeof raw.worker_id === "string" && mounted) {
            const wId = raw.worker_id as string;
            setSensorByWorker((prev) => ({
              ...prev,
              [wId]: {
                temp: typeof raw.temp === "number" ? raw.temp : undefined,
                accel_mag: typeof raw.accel_mag === "number" ? raw.accel_mag : undefined,
                ts: typeof raw.ts === "number" ? raw.ts : Date.now(),
              },
            }));
            return;
          }

          if (raw.type === "device_status" && typeof raw.worker_id === "string" && mounted) {
            const wId = raw.worker_id as string;
            setMpuConnectedByWorker((prev) => ({
              ...prev,
              [wId]: raw.mpu_connected === true,
            }));
            return;
          }

          const msg = raw as unknown as WorkerState;
          if (msg.worker_id && mounted) {
            const ts = msg.updated_at ?? Date.now();
            const risk = !!(msg.risk_ergo || msg.risk_fatigue);
            const ev: ActivityEvent = {
              ts,
              worker_id: msg.worker_id,
              label: msg.current_state ?? "idle",
              risk,
            };
            const trimmed = [
              ...timelineRef.current.filter((e) => ts - e.ts < TIMELINE_WINDOW_MS),
              ev,
            ].slice(-MAX_TIMELINE_EVENTS);
            timelineRef.current = trimmed;

            setWorkers((prev) => ({
              ...prev,
              [msg.worker_id]: {
                worker_id: msg.worker_id,
                name: msg.name ?? msg.worker_id,
                current_state: msg.current_state ?? "idle",
                risk_ergo: msg.risk_ergo ?? false,
                risk_fatigue: msg.risk_fatigue ?? false,
                updated_at: ts,
              },
            }));
            setMpuConnectedByWorker((prev) => ({ ...prev, [msg.worker_id]: true }));
          }
        } catch {
          // ignore parse errors
        }
      };
    }

    connect();

    return () => {
      mounted = false;
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
        reconnectTimeoutRef.current = null;
      }
      ws?.close();
    };
  }, []);

  const [activityTimeline, setActivityTimeline] = useState<ActivityEvent[]>([]);

  const refreshTimeline = useCallback(() => {
    const now = Date.now();
    setActivityTimeline(
      [...timelineRef.current].filter((e) => now - e.ts <= TIMELINE_WINDOW_MS)
    );
  }, []);

  // Refresh timeline when workers change (i.e. new WebSocket message arrived)
  useEffect(() => {
    refreshTimeline();
  }, [workers, refreshTimeline]);

  return {
    workers: Object.values(workers),
    connected,
    activityTimeline,
    sensorByWorker,
    mpuConnectedByWorker,
  };
}
