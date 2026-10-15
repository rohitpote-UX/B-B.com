"use client";

import { useEffect, useState } from "react";
import { PenTool, CheckSquare, Sparkles, Send, ShieldCheck } from "lucide-react";

export default function ContentStudioPage() {
  const [drafts, setDrafts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editedCopy, setEditedCopy] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function fetchDrafts() {
    try {
      const res = await fetch("/api/intelligence/content");
      const data = await res.json();
      if (res.ok) setDrafts(data.drafts || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchDrafts();
  }, []);

  async function handleSendToApproval(draftId: number) {
    setSubmitting(true);
    try {
      const res = await fetch(`/api/intelligence/content/${draftId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content_status: "READY_FOR_REVIEW" })
      });
      if (res.ok) {
        await fetchDrafts();
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
            Content Studio & AI Draft Generator
          </h1>
          <p style={{ fontSize: "14px", color: "var(--text-secondary)" }}>
            Synthesized marketing copy with evidence citation badges and strict safety gate verification.
          </p>
        </div>
      </div>

      {loading ? (
        <div style={{ textAlign: "center", padding: "60px 0", color: "var(--text-secondary)" }}>Loading content drafts...</div>
      ) : drafts.length === 0 ? (
        <div className="glass-card" style={{ padding: "40px", textAlign: "center", color: "var(--text-secondary)" }}>
          <PenTool size={32} style={{ color: "var(--text-dim)", marginBottom: "12px" }} />
          <p style={{ fontSize: "14px", fontWeight: 600 }}>No drafts generated yet. Visit Strategic Opportunities to generate copy.</p>
        </div>
      ) : (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(400px, 1fr))", gap: "20px" }}>
          {drafts.map((draft) => (
            <div key={draft.id} className="glass-card" style={{ padding: "24px" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "12px" }}>
                <span className="badge badge-verified" style={{ fontSize: "11px" }}>
                  Platform: {draft.platform?.toUpperCase() || draft.content_type}
                </span>

                <span className={`badge ${draft.verification_status === "VERIFIED" ? "badge-verified" : "badge-needs-review"}`}>
                  {draft.verification_status}
                </span>
              </div>

              <div style={{ marginBottom: "16px" }}>
                <textarea
                  rows={6}
                  className="bb-input"
                  value={editingId === draft.id ? editedCopy : draft.main_copy}
                  onChange={(e) => {
                    setEditingId(draft.id);
                    setEditedCopy(e.target.value);
                  }}
                  style={{ fontSize: "13px", lineHeight: "1.6", fontFamily: "sans-serif" }}
                />
              </div>

              {draft.evidence_summary && (
                <div style={{ fontSize: "12px", color: "var(--text-dim)", marginBottom: "16px", padding: "10px", background: "rgba(255,255,255,0.02)", borderRadius: "8px" }}>
                  🔍 <strong>Evidence Citation:</strong> {draft.evidence_summary}
                </div>
              )}

              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", borderTop: "1px solid var(--border)", paddingTop: "14px" }}>
                <span style={{ fontSize: "11px", color: "var(--text-dim)" }}>
                  Status: <strong style={{ color: "var(--text)" }}>{draft.content_status}</strong>
                </span>

                {draft.content_status !== "APPROVED" && (
                  <button
                    onClick={() => handleSendToApproval(draft.id)}
                    disabled={submitting}
                    className="btn-primary"
                    style={{ padding: "7px 14px", fontSize: "12px" }}
                  >
                    <Send size={13} />
                    Submit for Approval
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
