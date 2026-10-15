"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Lightbulb, Zap, ShieldCheck, PenTool, ArrowRight, AlertCircle } from "lucide-react";

export default function OpportunitiesPage() {
  const [findings, setFindings] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [generatingId, setGeneratingId] = useState<number | null>(null);
  const router = useRouter();

  async function fetchFindings() {
    try {
      const res = await fetch("/api/intelligence/findings");
      const data = await res.json();
      if (res.ok) setFindings(data.findings || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchFindings();
  }, []);

  async function generateDraft(findingId: number, contentType: string) {
    setGeneratingId(findingId);
    try {
      const res = await fetch("/api/intelligence/content", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ finding_id: findingId, content_type: contentType })
      });
      if (res.ok) {
        router.push("/dashboard/content");
      }
    } catch (err) {
      console.error(err);
    } finally {
      setGeneratingId(null);
    }
  }

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "24px" }}>
        <div>
          <h1 style={{ fontFamily: "Outfit, sans-serif", fontSize: "24px", fontWeight: 700, color: "var(--text)", marginBottom: "4px" }}>
            Strategic Opportunities & Signal Intelligence
          </h1>
          <p style={{ fontSize: "14px", color: "var(--text-secondary)" }}>
            Scored findings synthesized from verified market signals with actionable marketing recommendations.
          </p>
        </div>
      </div>

      {loading ? (
        <div style={{ textAlign: "center", padding: "60px 0", color: "var(--text-secondary)" }}>Loading findings...</div>
      ) : findings.length === 0 ? (
        <div className="glass-card" style={{ padding: "40px", textAlign: "center", color: "var(--text-secondary)" }}>
          <Lightbulb size={32} style={{ color: "var(--text-dim)", marginBottom: "12px" }} />
          <p style={{ fontSize: "14px", fontWeight: 600 }}>No strategic findings available yet.</p>
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
          {findings.map((item) => (
            <div key={item.id} className="glass-card" style={{ padding: "24px" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "12px" }}>
                <div>
                  <span className="badge badge-verified" style={{ fontSize: "11px", marginRight: "8px" }}>
                    Score: {item.total_score}/100
                  </span>
                  <span style={{ fontSize: "12px", color: "var(--gold)", fontWeight: 600 }}>
                    Urgency: {item.time_sensitivity || "MEDIUM"}
                  </span>
                </div>

                <div style={{ display: "flex", gap: "8px" }}>
                  <button
                    onClick={() => generateDraft(item.id, "x_post")}
                    disabled={generatingId === item.id}
                    className="btn-primary"
                    style={{ padding: "7px 14px", fontSize: "12px" }}
                  >
                    <PenTool size={13} />
                    {generatingId === item.id ? "Generating..." : "Generate X Post"}
                  </button>

                  <button
                    onClick={() => generateDraft(item.id, "instagram_caption")}
                    disabled={generatingId === item.id}
                    className="btn-secondary"
                    style={{ padding: "7px 14px", fontSize: "12px" }}
                  >
                    Generate IG Brief
                  </button>
                </div>
              </div>

              <h2 style={{ fontSize: "18px", fontWeight: 700, color: "var(--text)", marginBottom: "10px" }}>
                {item.title}
              </h2>

              <p style={{ fontSize: "14px", color: "var(--text-secondary)", lineHeight: "1.6", marginBottom: "16px" }}>
                {item.summary}
              </p>

              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px", marginBottom: "16px" }}>
                <div style={{ padding: "14px", borderRadius: "10px", background: "rgba(255,255,255,0.02)", border: "1px solid var(--border)" }}>
                  <div style={{ fontSize: "11px", fontWeight: 700, color: "var(--accent)", textTransform: "uppercase", marginBottom: "4px" }}>What Happened</div>
                  <div style={{ fontSize: "13px", color: "var(--text)", lineHeight: "1.5" }}>{item.what_happened}</div>
                </div>

                <div style={{ padding: "14px", borderRadius: "10px", background: "rgba(255,255,255,0.02)", border: "1px solid var(--border)" }}>
                  <div style={{ fontSize: "11px", fontWeight: 700, color: "var(--green)", textTransform: "uppercase", marginBottom: "4px" }}>Why It Matters for BrandBattle</div>
                  <div style={{ fontSize: "13px", color: "var(--text)", lineHeight: "1.5" }}>{item.why_it_matters}</div>
                </div>
              </div>

              {item.recommended_action && (
                <div style={{ padding: "12px 16px", borderRadius: "8px", background: "rgba(56,189,248,0.08)", border: "1px solid rgba(56,189,248,0.2)", fontSize: "13px", color: "#38bdf8" }}>
                  💡 <strong>Recommended Action:</strong> {item.recommended_action}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
