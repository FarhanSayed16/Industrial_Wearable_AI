/**
 * Industrial Wearable AI — Settings Page
 * Theme toggle, system info, and configuration.
 */
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { apiClient } from "../api/client";
import { configApi, type SystemConfigItem } from "../api/config";
import "./Settings.css";

type Theme = "light" | "dark" | "system";

function getStoredTheme(): Theme {
    return (localStorage.getItem("theme") as Theme) || "system";
}

function applyTheme(theme: Theme) {
    const html = document.documentElement;
    if (theme === "system") {
        const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
        html.setAttribute("data-theme", prefersDark ? "dark" : "light");
    } else {
        html.setAttribute("data-theme", theme);
    }
    localStorage.setItem("theme", theme);
}

export default function Settings() {
    const [theme, setTheme] = useState<Theme>(getStoredTheme);
    const [backendStatus, setBackendStatus] = useState<"checking" | "ok" | "error">("checking");
    const [backendVersion, setBackendVersion] = useState<string>("");
    const [configs, setConfigs] = useState<SystemConfigItem[]>([]);

    useEffect(() => {
        applyTheme(theme);
    }, [theme]);

    useEffect(() => {
        configApi.getAll().then(res => setConfigs(res.data)).catch(() => { /* ignore */ });
    }, []);

    useEffect(() => {
        let cancelled = false;
        (async () => {
            try {
                const [health, version] = await Promise.all([
                    apiClient.get("/health"),
                    apiClient.get("/api/version"),
                ]);
                if (!cancelled) {
                    setBackendStatus(health.data?.status === "ok" ? "ok" : "error");
                    setBackendVersion(version.data?.version ?? "unknown");
                }
            } catch {
                if (!cancelled) setBackendStatus("error");
            }
        })();
        return () => { cancelled = true; };
    }, []);

    const statusEmoji = backendStatus === "ok" ? "🟢" : backendStatus === "error" ? "🔴" : "🟡";

    return (
        <div className="settings-page">
            <h1 className="settings-title">Settings</h1>

            {/* Theme */}
            <section className="settings-card">
                <h2 className="settings-card-title">Appearance</h2>
                <div className="settings-theme-group">
                    {(["light", "dark", "system"] as Theme[]).map((t) => (
                        <button
                            key={t}
                            className={`settings-theme-btn ${theme === t ? "settings-theme-btn--active" : ""}`}
                            onClick={() => setTheme(t)}
                        >
                            {t === "light" ? "☀️" : t === "dark" ? "🌙" : "💻"}{" "}
                            {t.charAt(0).toUpperCase() + t.slice(1)}
                        </button>
                    ))}
                </div>
            </section>

            {/* System Info */}
            <section className="settings-card">
                <h2 className="settings-card-title">System Status</h2>
                <div className="settings-info-grid">
                    <div className="settings-info-item">
                        <span className="settings-info-label">Backend</span>
                        <span className="settings-info-value">{statusEmoji} {backendStatus}</span>
                    </div>
                    <div className="settings-info-item">
                        <span className="settings-info-label">API Version</span>
                        <span className="settings-info-value">{backendVersion || "—"}</span>
                    </div>
                    <div className="settings-info-item">
                        <span className="settings-info-label">Dashboard</span>
                        <span className="settings-info-value">v0.1.0</span>
                    </div>
                    <div className="settings-info-item">
                        <span className="settings-info-label">WebSocket</span>
                        <span className="settings-info-value">
                            {statusEmoji} {backendStatus === "ok" ? "Connected" : "Disconnected"}
                        </span>
                    </div>
                </div>
            </section>

            {/* Account */}
            <section className="settings-card">
                <h2 className="settings-card-title">Account</h2>
                <div className="settings-account-actions">
                    <Link to="/settings/password" className="settings-action-btn">
                        Change Password
                    </Link>
                </div>
            </section>

            {/* System Config */}
            <section className="settings-card">
                <h2 className="settings-card-title">Threshold Configuration (Admin)</h2>
                {configs.length === 0 ? (
                    <p className="settings-about-text">No configurations found or insufficient permissions.</p>
                ) : (
                    <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
                        {configs.map((c) => (
                            <div key={c.key} style={{ display: "flex", alignItems: "center", justifyContent: "space-between", paddingBottom: "0.5rem", borderBottom: "1px solid var(--color-border)" }}>
                                <div>
                                    <strong>{c.key}</strong>
                                    <p style={{ margin: 0, fontSize: "0.8rem", color: "var(--color-text-muted)" }}>{c.description}</p>
                                </div>
                                <div>
                                    <input
                                        type="text"
                                        defaultValue={c.value}
                                        onBlur={(e) => {
                                            if (e.target.value !== c.value) {
                                                configApi.setConfig({ ...c, value: e.target.value });
                                            }
                                        }}
                                        style={{ padding: "0.4rem", borderRadius: "4px", border: "1px solid var(--color-border)", background: "var(--color-bg)" }}
                                    />
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </section>

            {/* About */}
            <section className="settings-card">
                <h2 className="settings-card-title">About</h2>
                <p className="settings-about-text">
                    <strong>Industrial Wearable AI</strong> — AI-powered wearable monitoring for industrial workers.
                    Tracks activity, detects ergonomic risks, and prevents fatigue injuries in real-time.
                </p>
                <p className="settings-about-text settings-about-muted">
                    Built with FastAPI · React · PostgreSQL · Recharts · ESP32 · BLE
                </p>
            </section>
        </div>
    );
}
