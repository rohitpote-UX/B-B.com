"use client";

import { useEffect, useState } from "react";
import { ShieldCheck, AlertTriangle, CheckCircle2, FileText, Plus } from "lucide-react";

export default function EvidenceReviewPage() {
  const [records, setRecords] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [newEvidence, setNewEvidence] = useState({
    primary_source_url: "",
    excerpt: "",
    direct_quote: "",
    author_attribution: "",
    source_type: "news_report"
  });
  const [submitting, setSubmitting] = useState(false);

  async function fetchEvidence() {
    try {
      const res = await fetch("/api/intelligence/evidence");
      const data = await res.json();
      if (res.ok) setRecords(data.records || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchEvidence();
  }, []);

  async function handleAddEvidence(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    try {
      const res = await fetch("/api/intelligence/evidence", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(newEvidence)
      });
      if (res.ok) {
        setShowAddModal(false);
        setNewEvidence({ primary_source_url: "", excerpt: "", direct_quote: "", author_attribution: "", source_type: "news_report" });
        await fetchEvidence();
      }
    } catch (err) {
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "24px" }}>
        <div>
          <h1 style={{ fontFamily: "Outfit, sans-serif", fontSize: "24px", fontWeight: 700, color: "var(--text)", marginBottom: "4px" }}>
            Evidence Vault & Claim Verification
          </h1>
          <p style={{ fontSize: "14px", color: "var(--text-secondary)" }}>
            Ground-truth citations, direct quotes, and verification state machines for every generated claim.
          </p>
        </div>

        <button onClick={() => setShowAddModal(true)} className="btn-primary" style={{ padding: "9px 16px", fontSize: "13px" }}>
          <Plus size={15} /> Add Citation Evidence
        </button>
      </div>

      {showAddModal && (
        <div style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.7)", zIndex: 100, display: "flex", alignItems: "center", justifyContent: "center", padding: "20px" }}>
          <div className="glass-card" style={{ width: "100%", maxWidth: "520px", padding: "28px" }}>
            <h2 style={{ fontFamily: "Outfit, sans-serif", fontSize: "18px", fontWeight: 700, marginBottom: "16px", color: "var(--text)" }}>
              Add Evidence Record
            </h2>
            <form onSubmit={handleAddEvidence}>
              <div style={{ marginBottom: "12px" }}>
                <label style={{ display: "block", fontSize: "12px", color: "var(--text-secondary)", marginBottom: "4px" }}>Primary Source URL</label>
                <input
                  type="url"
                  required
                  placeholder="https://official-brand.com/press-release"
                  className="bb-input"
                  value={newEvidence.primary_source_url}
                  onChange={(e) => setNewEvidence({ ...newEvidence, primary_source_url: e.target.value })}
                />
              </div>

              <div style={{ marginBottom: "12px" }}>
                <label style={{ display: "block", fontSize: "12px", color: "var(--text-secondary)", marginBottom: "4px" }}>Direct Quote / Excerpt</label>
                <textarea
                  rows={3}
                  placeholder="Exact quote from source article..."
                  className="bb-input"
                  value={newEvidence.direct_quote}
                  onChange={(e) => setNewEvidence({ ...newEvidence, direct_quote: e.target.value })}
                />
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px", marginBottom: "16px" }}>
                <div>
                  <label style={{ display: "block", fontSize: "12px", color: "var(--text-secondary)", marginBottom: "4px" }}>Author / Publisher</label>
                  <input
                    type="text"
                    placeholder="e.g. Retail Bureau"
                    className="bb-input"
                    value={newEvidence.author_attribution}
                    onChange={(e) => setNewEvidence({ ...newEvidence, author_attribution: e.target.value })}
                  />
                </div>

                <div>
                  <label style={{ display: "block", fontSize: "12px", color: "var(--text-secondary)", marginBottom: "4px" }}>Source Type</label>
                  <select
                    className="bb-input"
                    value={newEvidence.source_type}
                    onChange={(e) => setNewEvidence({ ...newEvidence, source_type: e.target.value })}
                  >
                    <option value="official_press">Official Press Release</option>
                    <option value="news_report">News Report</option>
                    <option value="review_article">Review Article</option>
                    <option value="social_post">Verified Social Post</option>
                  </select>
                </div>
              </div>

              <div style={{ display: "flex", justifyContent: "flex-end", gap: "8px" }}>
                <button type="button" onClick={() => setShowAddModal(false)} className="btn-secondary" style={{ fontSize: "13px" }}>
                  Cancel
                </button>
                <button type="submit" disabled={submitting} className="btn-primary" style={{ fontSize: "13px" }}>
                  {submitting ? "Saving..." : "Save Record"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {loading ? (
        <div style={{ textAlign: "center", padding: "60px 0", color: "var(--text-secondary)" }}>Loading evidence records...</div>
      ) : records.length === 0 ? (
        <div className="glass-card" style={{ padding: "40px", textAlign: "center", color: "var(--text-secondary)" }}>
          <ShieldCheck size={32} style={{ color: "var(--text-dim)", marginBottom: "12px" }} />
          <p style={{ fontSize: "14px", fontWeight: 600 }}>No evidence records registered yet.</p>
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
          {records.map((rec) => (
            <div key={rec.id} className="glass-card" style={{ padding: "20px" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "12px" }}>
                <div>
                  <span className={`badge ${rec.verification_status === "VERIFIED" ? "badge-verified" : rec.verification_status === "CONTRADICTED" ? "badge-needs-review" : "badge-draft"}`}>
                    {rec.verification_status || "UNVERIFIED"}
                  </span>
                  <span style={{ fontSize: "12px", color: "var(--text-dim)", marginLeft: "10px" }}>
                    Corroboration Score: <strong style={{ color: "var(--text)" }}>{rec.corroboration_score}/100</strong>
                  </span>
                </div>

                <div style={{ fontSize: "11px", color: "var(--text-dim)" }}>
                  Verified by: {rec.verified_by || "System"}
                </div>
              </div>

              {rec.claim_text && (
                <div style={{ padding: "10px 14px", borderRadius: "8px", background: "rgba(242,10,176,0.06)", borderLeft: "3px solid var(--accent)", marginBottom: "12px", fontSize: "13px", fontWeight: 500, color: "var(--text)" }}>
                  Claim: &quot;{rec.claim_text}&quot;
                </div>
              )}

              {rec.direct_quote && (
                <blockquote style={{ fontSize: "13px", color: "var(--text-secondary)", fontStyle: "italic", borderLeft: "2px solid var(--border)", paddingLeft: "12px", marginBottom: "12px" }}>
                  &quot;{rec.direct_quote}&quot;
                </blockquote>
              )}

              <div style={{ fontSize: "12px", color: "var(--text-dim)", borderTop: "1px solid var(--border)", paddingTop: "10px", display: "flex", justifyContent: "space-between" }}>
                <span>Source: {rec.author_attribution || "Unknown Author"} ({rec.source_type})</span>
                <a href={rec.primary_source_url} target="_blank" rel="noopener noreferrer" style={{ color: "var(--accent)", textDecoration: "none" }}>
                  Link to Source →
                </a>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
