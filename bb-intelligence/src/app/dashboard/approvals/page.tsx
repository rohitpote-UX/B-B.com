"use client";

import { useEffect, useState } from "react";
import { CheckSquare, CheckCircle, XCircle, Edit3, ShieldAlert } from "lucide-react";

export default function ApprovalQueuePage() {
  const [drafts, setDrafts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionId, setActionId] = useState<number | null>(null);
  const [reviewerNotes, setReviewerNotes] = useState("");
  const [errorMsg, setErrorMsg] = useState("");

  async function fetchPendingDrafts() {
    try {
      const res = await fetch("/api/intelligence/content?status=READY_FOR_REVIEW");
      const data = await res.json();
      if (res.ok) setDrafts(data.drafts || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchPendingDrafts();
  }, []);

  async function handleDecision(draftId: number, decision: "APPROVED" | "REJECTED" | "NEEDS_EDITS") {
    setActionId(draftId);
    setErrorMsg("");
    try {
      const res = await fetch("/api/intelligence/approvals", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          draft_id: draftId,
          decision,
          reviewer_notes: reviewerNotes || `Human operator decision: ${decision}`
        })
      });
      const json = await res.json();
      if (!res.ok) {
        setErrorMsg(json.error || "Decision rejected by safety gate.");
        return;
      }
      await fetchPendingDrafts();
    } catch (err) {
      setErrorMsg("Failed to submit approval decision.");
    } finally {
      setActionId(null);
    }
  }

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "24px" }}>
        <div>
          <h1 style={{ fontFamily: "Outfit, sans-serif", fontSize: "24px", fontWeight: 700, color: "var(--text)", marginBottom: "4px" }}>
            Human Approval Queue & Safety Gates
          </h1>
          <p style={{ fontSize: "14px", color: "var(--text-secondary)" }}>
            Mandatory human-in-the-loop review step for all external marketing copy before publishing.
          </p>
        </div>
      </div>

      {errorMsg && (
        <div style={{ padding: "12px 16px", borderRadius: "8px", background: "rgba(248,113,113,0.1)", border: "1px solid rgba(248,113,113,0.3)", color: "#f87171", fontSize: "13px", marginBottom: "20px", display: "flex", alignItems: "center", gap: "8px" }}>
          <ShieldAlert size={16} />
          <span>{errorMsg}</span>
        </div>
      )}

      {loading ? (
        <div style={{ textAlign: "center", padding: "60px 0", color: "var(--text-secondary)" }}>Loading approval queue...</div>
      ) : drafts.length === 0 ? (
        <div className="glass-card" style={{ padding: "40px", textAlign: "center", color: "var(--text-secondary)" }}>
          <CheckSquare size={32} style={{ color: "var(--text-dim)", marginBottom: "12px" }} />
          <p style={{ fontSize: "14px", fontWeight: 600 }}>Queue is clear! No items awaiting review.</p>
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
          {drafts.map((draft) => (
            <div key={draft.id} className="glass-card" style={{ padding: "24px" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "12px" }}>
                <div>
                  <span className="badge badge-needs-review" style={{ fontSize: "11px", marginRight: "8px" }}>
                    Platform: {draft.platform?.toUpperCase()}
                  </span>
                  <span className={`badge ${draft.verification_status === "VERIFIED" ? "badge-verified" : "badge-needs-review"}`}>
                    Verification: {draft.verification_status}
                  </span>
                </div>

                <span style={{ fontSize: "12px", color: "var(--text-dim)" }}>
                  Draft #{draft.id}
                </span>
              </div>

              <div style={{ padding: "16px", borderRadius: "8px", background: "rgba(255,255,255,0.02)", border: "1px solid var(--border)", fontSize: "14px", color: "var(--text)", lineHeight: "1.6", marginBottom: "16px" }}>
                {draft.main_copy}
              </div>

              {draft.evidence_summary && (
                <div style={{ fontSize: "12px", color: "var(--text-dim)", marginBottom: "16px" }}>
                  <strong>Ground Truth Evidence:</strong> {draft.evidence_summary}
                </div>
              )}

              <div style={{ display: "flex", justifyContent: "flex-end", gap: "10px", borderTop: "1px solid var(--border)", paddingTop: "16px" }}>
                <button
                  onClick={() => handleDecision(draft.id, "REJECTED")}
                  disabled={actionId === draft.id}
                  className="btn-secondary"
                  style={{ color: "#f87171", borderColor: "rgba(248,113,113,0.3)", padding: "8px 16px", fontSize: "13px" }}
                >
                  <XCircle size={14} /> Reject
                </button>

                <button
                  onClick={() => handleDecision(draft.id, "NEEDS_EDITS")}
                  disabled={actionId === draft.id}
                  className="btn-secondary"
                  style={{ color: "var(--gold)", borderColor: "rgba(234,179,8,0.3)", padding: "8px 16px", fontSize: "13px" }}
                >
                  <Edit3 size={14} /> Request Edits
                </button>

                <button
                  onClick={() => handleDecision(draft.id, "APPROVED")}
                  disabled={actionId === draft.id}
                  className="btn-primary"
                  style={{ padding: "8px 18px", fontSize: "13px" }}
                >
                  <CheckCircle size={14} /> Approve & Authorize
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
