import { useCallback, useEffect, useState } from "react";
import { getWorkers, type WorkerOut as Worker } from "../api/workers";
import { getWorkerConsent, updateWorkerConsent, purgeWorkerData, type ConsentRecord } from "../api/privacy";
import { Shield, AlertTriangle, CheckCircle, XCircle } from "lucide-react";
import "./Privacy.css";

export default function Privacy() {
    const [workers, setWorkers] = useState<Worker[]>([]);
    const [selectedWorkerId, setSelectedWorkerId] = useState<string>("");
    const [consent, setConsent] = useState<ConsentRecord | null>(null);
    const [loading, setLoading] = useState(false);

    // Form state
    const [retentionDays, setRetentionDays] = useState<string>("365");
    const [optData, setOptData] = useState<boolean>(true);
    const [optAI, setOptAI] = useState<boolean>(true);

    const [saving, setSaving] = useState(false);
    const [purging, setPurging] = useState(false);

    useEffect(() => {
        getWorkers().then(setWorkers).catch(console.error);
    }, []);

    const loadConsent = useCallback(async (id: string) => {
        if (!id) {
            setConsent(null);
            return;
        }
        setLoading(true);
        try {
            const data = await getWorkerConsent(id);
            setConsent(data);
            if (data.status === "consented") {
                setRetentionDays(data.retention_days || "365");
                setOptData(data.opt_in_data_collection);
                setOptAI(data.opt_in_ai_analysis || true);
            } else {
                setRetentionDays("365");
                setOptData(false);
                setOptAI(false);
            }
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    }, []);

    const handleSelect = (e: React.ChangeEvent<HTMLSelectElement>) => {
        const id = e.target.value;
        setSelectedWorkerId(id);
        loadConsent(id);
    };

    const handleSave = async () => {
        if (!selectedWorkerId) return;
        setSaving(true);
        try {
            await updateWorkerConsent(selectedWorkerId, {
                retention_days: retentionDays,
                opt_in_data_collection: optData,
                opt_in_ai_analysis: optAI,
            });
            await loadConsent(selectedWorkerId);
            alert("Privacy settings updated successfully.");
        } catch (err) {
            alert("Failed to update privacy settings.");
        } finally {
            setSaving(false);
        }
    };

    const handlePurge = async () => {
        if (!selectedWorkerId) return;
        const confirmMsg = "CRITICAL WARNING: This will permanently delete ALL session and sensor data for this worker. This implements the Right to Deletion. Are you absolutely sure?";
        if (!window.confirm(confirmMsg)) return;

        setPurging(true);
        try {
            const result = await purgeWorkerData(selectedWorkerId);
            alert(`Purged successfully.\\nDeleted Events: ${result.deleted_events}\\nDeleted Sessions: ${result.deleted_sessions}`);
        } catch (err) {
            alert("Failed to purge data.");
        } finally {
            setPurging(false);
        }
    };

    return (
        <div className="privacy-page" style={{ padding: "2rem", maxWidth: "800px", margin: "0 auto" }}>
            <h1 style={{ display: "flex", alignItems: "center", gap: "0.75rem", fontSize: "1.8rem", color: "#1e293b", marginBottom: "2rem" }}>
                <Shield size={32} color="#3b82f6" /> Privacy & Consent Management
            </h1>

            <div style={{ background: "white", padding: "1.5rem", borderRadius: "8px", border: "1px solid #e2e8f0", marginBottom: "2rem" }}>
                <label style={{ display: "block", marginBottom: "0.5rem", fontWeight: 600, color: "#475569" }}>Select Worker</label>
                <select
                    value={selectedWorkerId}
                    onChange={handleSelect}
                    style={{ width: "100%", padding: "0.75rem", borderRadius: "6px", border: "1px solid #cbd5e1" }}
                >
                    <option value="">-- Choose a worker --</option>
                    {workers.map(w => (
                        <option key={w.id} value={w.id}>{w.name} ({w.role || "No role"})</option>
                    ))}
                </select>
            </div>

            {loading && <p>Loading consent record...</p>}

            {selectedWorkerId && !loading && consent && (
                <div style={{ background: "white", padding: "2rem", borderRadius: "8px", border: "1px solid #e2e8f0", boxShadow: "0 1px 3px rgba(0,0,0,0.05)" }}>
                    <div style={{ display: "flex", alignItems: "center", gap: "1rem", marginBottom: "2rem", paddingBottom: "1rem", borderBottom: "1px solid #e2e8f0" }}>
                        {consent.status === "consented" ? (
                            <><CheckCircle size={28} color="#10b981" /> <div><h3 style={{ margin: 0 }}>Consent on File</h3><p style={{ margin: 0, color: "#64748b", fontSize: "0.9rem" }}>Provided on {new Date(consent.consented_at!).toLocaleDateString()}</p></div></>
                        ) : (
                            <><XCircle size={28} color="#ef4444" /> <h3 style={{ margin: 0 }}>No Consent Record</h3></>
                        )}
                    </div>

                    <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
                        <div>
                            <label style={{ display: "flex", alignItems: "center", gap: "0.75rem", cursor: "pointer", fontWeight: 500 }}>
                                <input type="checkbox" checked={optData} onChange={e => setOptData(e.target.checked)} style={{ width: "1.2rem", height: "1.2rem" }} />
                                Opt-in to general activity and biometric data collection
                            </label>
                            <p style={{ margin: "0.25rem 0 0 2rem", fontSize: "0.85rem", color: "#64748b" }}>Required for the wearable to function and transmit telemetry.</p>
                        </div>

                        <div>
                            <label style={{ display: "flex", alignItems: "center", gap: "0.75rem", cursor: "pointer", fontWeight: 500 }}>
                                <input type="checkbox" checked={optAI} onChange={e => setOptAI(e.target.checked)} style={{ width: "1.2rem", height: "1.2rem" }} />
                                Opt-in to AI Root-Cause Analysis
                            </label>
                            <p style={{ margin: "0.25rem 0 0 2rem", fontSize: "0.85rem", color: "#64748b" }}>Allows automated correlation of behavior to environmental factors.</p>
                        </div>

                        <div>
                            <label style={{ display: "block", marginBottom: "0.5rem", fontWeight: 500 }}>Data Retention Policy</label>
                            <select value={retentionDays} onChange={e => setRetentionDays(e.target.value)} style={{ padding: "0.5rem", borderRadius: "6px", border: "1px solid #cbd5e1" }}>
                                <option value="30">30 Days</option>
                                <option value="90">90 Days</option>
                                <option value="365">1 Year (365 Days)</option>
                                <option value="indefinite">Indefinite (Until manually purged)</option>
                            </select>
                            <p style={{ margin: "0.25rem 0 0 0", fontSize: "0.85rem", color: "#64748b" }}>Automatically anonymize data older than this limit (Requires cron setup).</p>
                        </div>
                    </div>

                    <div style={{ marginTop: "2rem", display: "flex", gap: "1rem" }}>
                        <button
                            onClick={handleSave}
                            disabled={saving}
                            style={{ background: "#3b82f6", color: "white", border: "none", padding: "0.75rem 1.5rem", borderRadius: "6px", fontWeight: 600, cursor: "pointer" }}
                        >
                            {saving ? "Saving..." : "Save Privacy Settings"}
                        </button>
                    </div>

                    <div style={{ marginTop: "3rem", paddingTop: "2rem", borderTop: "2px solid #fee2e2" }}>
                        <h3 style={{ display: "flex", alignItems: "center", gap: "0.5rem", color: "#b91c1c", marginTop: 0 }}>
                            <AlertTriangle size={20} /> Right to Deletion (GDPR/CCPA)
                        </h3>
                        <p style={{ color: "#7f1d1d", fontSize: "0.9rem" }}>Immediately purges all historical session logs, activities, and aggregated metrics for this user.</p>
                        <button
                            onClick={handlePurge}
                            disabled={purging}
                            style={{ background: "#ef4444", color: "white", border: "none", padding: "0.75rem 1.5rem", borderRadius: "6px", fontWeight: 600, cursor: "pointer", display: "flex", alignItems: "center", gap: "0.5rem" }}
                        >
                            {purging ? "Purging..." : "Permanently Delete Data"}
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}
