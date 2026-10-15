"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  Zap,
  Newspaper,
  Database,
  ShieldCheck,
  Lightbulb,
  CheckSquare,
  RefreshCw,
  ArrowRight,
  TrendingUp,
  AlertCircle
} from "lucide-react";

export default function OverviewPage() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [runningJob, setRunningJob] = useState(false);
  const [jobMessage, setJobMessage] = useState("");

  async function fetchOverview() {
    try {
      const res = await fetch("/api/intelligence/overview");
      const d = await res.json();
      if (res.ok) setData(d);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchOverview();
  }, []);

  async function triggerCollection() {
    setRunningJob(true);
    setJobMessage("Running intelligence gathering collectors...");
    try {
      const res = await fetch("/api/intelligence/jobs", { method: "POST" });
      const json = await res.json();
      if (res.ok) {
        setJobMessage("Collection complete! Signal catalog updated.");
        await fetchOverview();
      } else {
        setJobMessage(`Error: ${json.error || "Job failed"}`);
      }
    } catch {
      setJobMessage("Failed to execute collector job.");
    } finally {
      setRunningJob(false);
    }
  }

  if (loading) {
    return (
      <div style={{ display: "flex", justifyContent: "center", padding: "60px 0" }}>
        <div style={{ color: "var(--text-secondary)", fontSize: "14px" }}>Loading intelligence metrics...</div>
      </div>
    );
  }

  const stats = data?.stats || {};
  const recentItems = data?.recent_items || [];
  const recentFindings = data?.recent_findings || [];

  return (
    <div>
      {/* Header section */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "24px" }}>
        <div>
          <h1 style={{ fontFamily: "Outfit, sans-serif", fontSize: "26px", fontWeight: 700, color: "var(--text)", marginBottom: "4px" }}>
            Intelligence Operations Center
          </h1>
          <p style={{ fontSize: "14px", color: "var(--text-secondary)" }}>
            Real-time market signals, evidence verification, and AI content synthesis for BrandBattle.
          </p>
        </div>

        <button
          onClick={triggerCollection}
          disabled={runningJob}
          className="btn-primary"
          style={{ padding: "10px 18px", fontSize: "13px" }}
        >
          <RefreshCw size={14} className={runningJob ? "spin" : ""} />
          {runningJob ? "Gathering Signals..." : "Run Intelligence Collector"}
        </button>
      </div>

      {jobMessage && (
        <div style={{ padding: "12px 16px", borderRadius: "8px", background: "rgba(242,10,176,0.1)", border: "1px solid rgba(242,10,176,0.3)", color: "var(--accent)", fontSize: "13px", marginBottom: "24px", display: "flex", alignItems: "center", gap: "8px" }}>
          <Zap size={14} />
          <span>{jobMessage}</span>
        </div>
      )}

      {/* KPI Cards Grid */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "16px", marginBottom: "32px" }}>
        <div className="glass-card" style={{ padding: "20px" }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", color: "var(--text-secondary)", fontSize: "12px", marginBottom: "8px" }}>
            <span>Active Feed Sources</span>
            <Database size={16} style={{ color: "var(--accent)" }} />
          </div>
          <div style={{ fontSize: "28px", fontWeight: 800, color: "var(--text)", fontFamily: "Outfit, sans-serif" }}>
            {stats.active_sources || 0}
          </div>
          <div style={{ fontSize: "11px", color: "var(--green)", marginTop: "4px" }}>Connected & Monitoring</div>
        </div>

        <div className="glass-card" style={{ padding: "20px" }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", color: "var(--text-secondary)", fontSize: "12px", marginBottom: "8px" }}>
            <span>Research Items</span>
            <Newspaper size={16} style={{ color: "#38bdf8" }} />
          </div>
          <div style={{ fontSize: "28px", fontWeight: 800, color: "var(--text)", fontFamily: "Outfit, sans-serif" }}>
            {stats.total_items || 0}
          </div>
          <div style={{ fontSize: "11px", color: "var(--text-secondary)", marginTop: "4px" }}>Processed Signals</div>
        </div>

        <div className="glass-card" style={{ padding: "20px" }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", color: "var(--text-secondary)", fontSize: "12px", marginBottom: "8px" }}>
            <span>High-Value Opportunities</span>
            <Lightbulb size={16} style={{ color: "var(--gold)" }} />
          </div>
          <div style={{ fontSize: "28px", fontWeight: 800, color: "var(--text)", fontFamily: "Outfit, sans-serif" }}>
            {stats.active_findings || 0}
          </div>
          <div style={{ fontSize: "11px", color: "var(--gold)", marginTop: "4px" }}>Actionable Signals</div>
        </div>

        <div className="glass-card" style={{ padding: "20px" }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", color: "var(--text-secondary)", fontSize: "12px", marginBottom: "8px" }}>
            <span>Pending Approvals</span>
            <CheckSquare size={16} style={{ color: "#a855f7" }} />
          </div>
          <div style={{ fontSize: "28px", fontWeight: 800, color: "var(--text)", fontFamily: "Outfit, sans-serif" }}>
            {stats.pending_approvals || 0}
          </div>
          <div style={{ fontSize: "11px", color: stats.pending_approvals > 0 ? "#f87171" : "var(--text-secondary)", marginTop: "4px" }}>
            {stats.pending_approvals > 0 ? "Requires Review" : "Queue Clean"}
          </div>
        </div>
      </div>

      {/* Main Grid: Recent Intelligence Findings & Signal Feed */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "24px" }}>
        {/* Top Opportunities */}
        <div className="glass-card" style={{ padding: "24px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
            <h2 style={{ fontFamily: "Outfit, sans-serif", fontSize: "16px", fontWeight: 700, color: "var(--text)", display: "flex", alignItems: "center", gap: "8px" }}>
              <TrendingUp size={16} style={{ color: "var(--accent)" }} />
              Top Strategic Findings
            </h2>
            <Link href="/dashboard/opportunities" style={{ fontSize: "12px", color: "var(--accent)", textDecoration: "none", display: "flex", alignItems: "center", gap: "4px" }}>
              View all <ArrowRight size={12} />
            </Link>
          </div>

          {recentFindings.length === 0 ? (
            <div style={{ padding: "30px 0", textAlign: "center", color: "var(--text-secondary)", fontSize: "13px" }}>
              No intelligence findings generated yet. Run the collector to ingest signals.
            </div>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
              {recentFindings.map((finding: any) => (
                <div
                  key={finding.id}
                  style={{
                    padding: "14px",
                    borderRadius: "10px",
                    background: "rgba(255,255,255,0.02)",
                    border: "1px solid var(--border)",
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "6px" }}>
                    <span className="badge badge-verified" style={{ fontSize: "10px" }}>
                      Score: {finding.total_score}/100
                    </span>
                    <span style={{ fontSize: "11px", color: "var(--text-dim)" }}>
                      Urgency: {finding.time_sensitivity}
                    </span>
                  </div>
                  <h3 style={{ fontSize: "14px", fontWeight: 600, color: "var(--text)", marginBottom: "4px" }}>
                    {finding.title}
                  </h3>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Live Signal Feed */}
        <div className="glass-card" style={{ padding: "24px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
            <h2 style={{ fontFamily: "Outfit, sans-serif", fontSize: "16px", fontWeight: 700, color: "var(--text)", display: "flex", alignItems: "center", gap: "8px" }}>
              <Newspaper size={16} style={{ color: "#38bdf8" }} />
              Latest Ingested Signals
            </h2>
            <Link href="/dashboard/research" style={{ fontSize: "12px", color: "var(--accent)", textDecoration: "none", display: "flex", alignItems: "center", gap: "4px" }}>
              Feed <ArrowRight size={12} />
            </Link>
          </div>

          {recentItems.length === 0 ? (
            <div style={{ padding: "30px 0", textAlign: "center", color: "var(--text-secondary)", fontSize: "13px" }}>
              No items collected yet. Click &quot;Run Intelligence Collector&quot; above.
            </div>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
              {recentItems.map((item: any) => (
                <div
                  key={item.id}
                  style={{
                    padding: "12px 14px",
                    borderRadius: "10px",
                    background: "rgba(255,255,255,0.02)",
                    border: "1px solid var(--border)",
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", fontSize: "11px", color: "var(--text-secondary)", marginBottom: "4px" }}>
                    <span>{item.source_name || "RSS Feed"}</span>
                    <span style={{ color: "var(--accent)", fontWeight: 700 }}>Rel: {item.relevance_score}</span>
                  </div>
                  <div style={{ fontSize: "13px", color: "var(--text)", fontWeight: 500 }}>
                    {item.title}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
