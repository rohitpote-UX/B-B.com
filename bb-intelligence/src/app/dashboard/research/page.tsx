"use client";

import { useEffect, useState } from "react";
import { Newspaper, ExternalLink, Filter, Zap } from "lucide-react";

export default function ResearchFeedPage() {
  const [items, setItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [minScore, setMinScore] = useState("0");

  async function fetchItems() {
    setLoading(true);
    try {
      const query = minScore !== "0" ? `?min_score=${minScore}` : "";
      const res = await fetch(`/api/intelligence/research${query}`);
      const data = await res.json();
      if (res.ok) setItems(data.items || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchItems();
  }, [minScore]);

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "24px" }}>
        <div>
          <h1 style={{ fontFamily: "Outfit, sans-serif", fontSize: "24px", fontWeight: 700, color: "var(--text)", marginBottom: "4px" }}>
            Research Feed & Raw Signals
          </h1>
          <p style={{ fontSize: "14px", color: "var(--text-secondary)" }}>
            Normalized, deduplicated article stream from registered market intelligence sources.
          </p>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          <Filter size={14} style={{ color: "var(--text-secondary)" }} />
          <select
            value={minScore}
            onChange={(e) => setMinScore(e.target.value)}
            className="bb-input"
            style={{ padding: "8px 12px", fontSize: "13px" }}
          >
            <option value="0">All Relevance Scores</option>
            <option value="50">Min Relevance 50+</option>
            <option value="75">High Relevance 75+</option>
            <option value="90">Top Signal 90+</option>
          </select>
        </div>
      </div>

      {loading ? (
        <div style={{ textAlign: "center", padding: "60px 0", color: "var(--text-secondary)" }}>Loading research stream...</div>
      ) : items.length === 0 ? (
        <div className="glass-card" style={{ padding: "40px", textAlign: "center", color: "var(--text-secondary)" }}>
          <Newspaper size={32} style={{ color: "var(--text-dim)", marginBottom: "12px" }} />
          <p style={{ fontSize: "14px", fontWeight: 600 }}>No research items matching filter</p>
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
          {items.map((item) => (
            <div key={item.id} className="glass-card" style={{ padding: "20px" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "8px" }}>
                <div>
                  <span className="badge badge-verified" style={{ fontSize: "11px", marginRight: "8px" }}>
                    {item.source_name || "Feed"}
                  </span>
                  <span style={{ fontSize: "12px", color: "var(--text-dim)" }}>
                    {new Date(item.collected_at || Date.now()).toLocaleDateString()}
                  </span>
                </div>

                <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                  <span style={{ fontSize: "12px", fontWeight: 700, color: item.relevance_score >= 80 ? "var(--green)" : "var(--accent)" }}>
                    Score: {item.relevance_score}/100
                  </span>
                </div>
              </div>

              <h2 style={{ fontSize: "16px", fontWeight: 600, color: "var(--text)", marginBottom: "8px" }}>
                {item.title}
              </h2>

              <p style={{ fontSize: "13px", color: "var(--text-secondary)", lineHeight: "1.6", marginBottom: "16px" }}>
                {item.content || item.summary || "No extended snippet available."}
              </p>

              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", borderTop: "1px solid var(--border)", paddingTop: "12px" }}>
                <div style={{ fontSize: "11px", color: "var(--text-dim)" }}>
                  Processing: <strong style={{ color: "var(--text-secondary)" }}>{item.processing_status}</strong>
                </div>

                {item.link && (
                  <a
                    href={item.link}
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{ fontSize: "12px", color: "var(--accent)", textDecoration: "none", display: "inline-flex", alignItems: "center", gap: "4px" }}
                  >
                    View Original Source <ExternalLink size={12} />
                  </a>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
