/**
 * Industrial Wearable AI — Live Sensor Strip (Phase C)
 * Shows temp and movement from ESP32 per worker when sensor stream is enabled.
 */
import { Thermometer, Activity } from "lucide-react";
import type { WorkerState } from "../hooks/useWebSocket";
import type { SensorSnapshot } from "../hooks/useWebSocket";

interface LiveSensorStripProps {
  workers: WorkerState[];
  sensorByWorker: Record<string, SensorSnapshot>;
}

function movementLevel(accelMag: number): "low" | "medium" | "high" {
  if (accelMag < 2) return "low";
  if (accelMag < 6) return "medium";
  return "high";
}

function formatUpdated(ts: number): string {
  const sec = (Date.now() - ts) / 1000;
  if (sec < 15) return "just now";
  if (sec < 60) return `${Math.floor(sec)}s ago`;
  if (sec < 3600) return `${Math.floor(sec / 60)}m ago`;
  return new Date(ts).toLocaleTimeString();
}

export default function LiveSensorStrip({ workers, sensorByWorker }: LiveSensorStripProps) {
  if (workers.length === 0) return null;

  const hasAnySensor = workers.some((w) => sensorByWorker[w.worker_id]);
  if (!hasAnySensor) {
    return (
      <div className="live-sensor-strip live-sensor-strip-empty">
        <Thermometer size={16} />
        <span>Live sensor data from wearables will appear here (temp, movement) when the edge sends it.</span>
      </div>
    );
  }

  return (
    <div className="live-sensor-strip">
      <div className="live-sensor-strip-header">
        <Thermometer size={16} />
        <strong>Live sensor (from ESP32)</strong>
      </div>
      <div className="live-sensor-strip-grid">
        {workers.map((w) => {
          const sensor = sensorByWorker[w.worker_id];
          const tempStr = sensor?.temp != null ? `${sensor.temp} °C` : "—";
          const movement =
            sensor?.accel_mag != null ? movementLevel(sensor.accel_mag) : null;
          const updatedStr = sensor?.ts ? formatUpdated(sensor.ts) : "—";

          return (
            <div key={w.worker_id} className="live-sensor-card">
              <div className="live-sensor-card-name">{w.name}</div>
              <div className="live-sensor-card-row">
                <span className="live-sensor-label">Temp</span>
                <span className="live-sensor-value">{tempStr}</span>
              </div>
              <div className="live-sensor-card-row">
                <Activity size={12} className="live-sensor-icon" />
                <span className="live-sensor-label">Movement</span>
                <span
                  className={`live-sensor-value live-sensor-movement live-sensor-movement-${movement ?? "none"}`}
                >
                  {movement ? movement : "—"}
                </span>
              </div>
              <div className="live-sensor-card-updated">Updated {updatedStr}</div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
