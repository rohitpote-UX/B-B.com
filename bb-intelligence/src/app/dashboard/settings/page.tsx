"use client";

import { useEffect, useState } from "react";
import { Settings, ShieldCheck, Activity, Key, Database } from "lucide-react";

export default function SettingsPage() {
  const [logs, setLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  async function fetchAuditLogs() {
    try {
      const res = await fetch("/api/intelligence/audit");
      const data = await res.json();
      if (res.ok) setLogs(data.logs || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchAuditLogs();
  }, []);

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "24px" }}>
        <div>
          <h1 style={{ fontFamily: "Outfit, sans-serif", fontSize: "24px", fontWeight: 700, color: "var(--text)", marginBottom: "4px" }}>
            System Settings & Security Audit Logs
          </h1>
          <p style={{ fontSize: "14px", color: "var(--text-secondary)" }}>
            System health indicators, provider configuration status, and immutable audit logs.
          </p>
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "24px", marginBottom: "32px" }}>
        {/* System Configuration Status */}
        <div className="glass-card" style={{ padding: "24px" }}>
          <h2 style={{ fontFamily: "Outfit, sans-serif", fontSize: "16px", fontWeight: 700, color: "var(--text)", marginBottom: "16px", display: "flex", alignItems: "center", gap: "8px" }}>
            <Key size={16} style={{ color: "var(--accent)" }} /> Provider & Safety Configuration
          </h2>

          <div style={{ display: "flex", flexDirection: "column", gap: "12px", fontSize: "13px" }}>
            <div style={{ display: "flex", justifyContent: "space-between", borderBottom: "1px solid var(--border)", paddingBottom: "8px" }}>
              <span style={{ color: "var(--text-secondary)" }}>Database Engine</span>
              <span style={{ fontWeight: 600, color: "var(--green)" }}>Neon Postgres / Memory Driver</span>
            </div>

            <div style={{ display: "flex", justifyContent: "space-between", borderBottom: "1px solid var(--border)", paddingBottom: "8px" }}>
              <span style={{ color: "var(--text-secondary)" }}>LLM Generator Provider</span>
              <span style={{ fontWeight: 600, color: "var(--accent)" }}>Gemini 1.5 Flash / Mock Synthesizer</span>
            </div>

            <div style={{ display: "flex", justifyContent: "space-between", borderBottom: "1px solid var(--border)", paddingBottom: "8px" }}>
              <span style={{ color: "var(--text-secondary)" }}>SSRF Outbound Guard</span>
              <span style={{ fontWeight: 600, color: "var(--green)" }}>ENABLED (Strict Local Subnet Block)</span>
            </div>

            <div style={{ display: "flex", justifyContent: "space-between", paddingBottom: "4px" }}>
              <span style={{ color: "var(--text-secondary)" }}>Human Safety Gate</span>
              <span style={{ fontWeight: 600, color: "var(--green)" }}>ENABLED (Mandatory Operator Verification)</span>
            </div>
          </div>
        </div>

        {/* Intelligence Engine Thresholds */}
        <div className="glass-card" style={{ padding: "24px" }}>
          <h2 style={{ fontFamily: "Outfit, sans-serif", fontSize: "16px", fontWeight: 700, color: "var(--text)", marginBottom: "16px", display: "flex", alignItems: "center", gap: "8px" }}>
            <Activity size={16} style={{ color: "#38bdf8" }} /> Scoring & Urgency Parameters
          </h2>

          <div style={{ display: "flex", flexDirection: "column", gap: "12px", fontSize: "13px" }}>
            <div style={{ display: "flex", justifyContent: "space-between", borderBottom: "1px solid var(--border)", paddingBottom: "8px" }}>
              <span style={{ color: "var(--text-secondary)" }}>Brand Impact Weight</span>
              <span style={{ fontWeight: 600, color: "var(--text)" }}>35%</span>
            </div>

            <div style={{ display: "flex", justifyContent: "space-between", borderBottom: "1px solid var(--border)", paddingBottom: "8px" }}>
              <span style={{ color: "var(--text-secondary)" }}>Market Reach Weight</span>
              <span style={{ fontWeight: 600, color: "var(--text)" }}>25%</span>
            </div>

            <div style={{ display: "flex", justifyContent: "space-between", borderBottom: "1px solid var(--border)", paddingBottom: "8px" }}>
              <span style={{ color: "var(--text-secondary)" }}>Customer Relevance Weight</span>
              <span style={{ fontWeight: 600, color: "var(--text)" }}>25%</span>
            </div>

            <div style={{ display: "flex", justifyContent: "space-between", paddingBottom: "4px" }}>
              <span style={{ color: "var(--text-secondary)" }}>Strategic Urgency Weight</span>
              <span style={{ fontWeight: 600, color: "var(--text)" }}>15%</span>
            </div>
          </div>
        </div>
      </div>

      {/* Audit Log Table */}
      <div className="glass-card" style={{ padding: "24px" }}>
        <h2 style={{ fontFamily: "Outfit, sans-serif", fontSize: "16px", fontWeight: 700, color: "var(--text)", marginBottom: "16px", display: "flex", alignItems: "center", gap: "8px" }}>
          <ShieldCheck size={16} style={{ color: "var(--green)" }} /> Audit Log History
        </h2>

        {loading ? (
          <div style={{ textAlign: "center", padding: "30px 0", color: "var(--text-secondary)" }}>Loading logs...</div>
        ) : logs.length === 0 ? (
          <div style={{ textAlign: "center", padding: "30px 0", color: "var(--text-secondary)", fontSize: "13px" }}>No audit log entries recorded yet.</div>
        ) : (
          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "13px", color: "var(--text)" }}>
              <thead>
                <tr style={{ borderBottom: "1px solid var(--border)", textAlign: "left", color: "var(--text-secondary)", fontSize: "11px", textTransform: "uppercase" }}>
                  <th style={{ padding: "8px 12px" }}>Time</th>
                  <th style={{ padding: "8px 12px" }}>Action</th>
                  <th style={{ padding: "8px 12px" }}>Actor</th>
                  <th style={{ padding: "8px 12px" }}>Entity</th>
                  <th style={{ padding: "8px 12px" }}>IP Address</th>
                </tr>
              </thead>
              <tbody>
                {logs.map((log) => (
                  <tr key={log.id} style={{ borderBottom: "1px solid rgba(255,255,255,0.03)" }}>
                    <td style={{ padding: "10px 12px", color: "var(--text-dim)", fontSize: "12px" }}>
                      {new Date(log.created_at || Date.now()).toLocaleTimeString()}
                    </td>
                    <td style={{ padding: "10px 12px", fontWeight: 600, color: "var(--accent)" }}>{log.action}</td>
                    <td style={{ padding: "10px 12px" }}>{log.actor || "operator"}</td>
                    <td style={{ padding: "10px 12px", color: "var(--text-secondary)" }}>{log.entity_type || "system"}</td>
                    <td style={{ padding: "10px 12px", color: "var(--text-dim)", fontSize: "12px" }}>{log.ip_address || "127.0.0.1"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
