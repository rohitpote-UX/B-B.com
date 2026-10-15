"use client";

import { useEffect, useState } from "react";
import { Database, Plus, CheckCircle, XCircle, Trash2, Globe, RefreshCw } from "lucide-react";

export default function SourceRegistryPage() {
  const [sources, setSources] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [newSource, setNewSource] = useState({
    name: "",
    category: "competitor",
    url: "",
    frequency_hours: "6",
  });
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function fetchSources() {
    try {
      const res = await fetch("/api/intelligence/sources");
      const data = await res.json();
      if (res.ok) setSources(data.sources || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchSources();
  }, []);

  async function handleAddSource(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    setError("");

    try {
      const res = await fetch("/api/intelligence/sources", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(newSource),
      });
      const data = await res.json();

      if (!res.ok) {
        setError(data.error || "Failed to add source.");
        return;
      }

      setShowAddModal(false);
      setNewSource({ name: "", category: "competitor", url: "", frequency_hours: "6" });
      await fetchSources();
    } catch {
      setError("Network error adding source.");
    } finally {
      setSubmitting(false);
    }
  }

  async function handleDeleteSource(id: number) {
    if (!confirm("Are you sure you want to remove this source?")) return;
    try {
      await fetch(`/api/intelligence/sources/${id}`, { method: "DELETE" });
      await fetchSources();
    } catch (err) {
      console.error(err);
    }
  }

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "24px" }}>
        <div>
          <h1 style={{ fontFamily: "Outfit, sans-serif", fontSize: "24px", fontWeight: 700, color: "var(--text)", marginBottom: "4px" }}>
            Source Registry & Ingestion Catalog
          </h1>
          <p style={{ fontSize: "14px", color: "var(--text-secondary)" }}>
            Registered RSS feeds, competitor watchlists, and market scanners.
          </p>
        </div>

        <button onClick={() => setShowAddModal(true)} className="btn-primary" style={{ padding: "9px 16px", fontSize: "13px" }}>
          <Plus size={15} /> Add Intelligence Source
        </button>
      </div>

      {showAddModal && (
        <div style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.7)", zIndex: 100, display: "flex", alignItems: "center", justifyContent: "center", padding: "20px" }}>
          <div className="glass-card" style={{ width: "100%", maxWidth: "500px", padding: "28px" }}>
            <h2 style={{ fontFamily: "Outfit, sans-serif", fontSize: "18px", fontWeight: 700, marginBottom: "16px", color: "var(--text)" }}>
              Add Intelligence Source
            </h2>

            <form onSubmit={handleAddSource}>
              <div style={{ marginBottom: "12px" }}>
                <label style={{ display: "block", fontSize: "12px", color: "var(--text-secondary)", marginBottom: "4px" }}>Source Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Retail Trends India RSS"
                  className="bb-input"
                  value={newSource.name}
                  onChange={(e) => setNewSource({ ...newSource, name: e.target.value })}
                />
              </div>

              <div style={{ marginBottom: "12px" }}>
                <label style={{ display: "block", fontSize: "12px", color: "var(--text-secondary)", marginBottom: "4px" }}>Feed / Article URL</label>
                <input
                  type="url"
                  required
                  placeholder="https://example.com/rss"
                  className="bb-input"
                  value={newSource.url}
                  onChange={(e) => setNewSource({ ...newSource, url: e.target.value })}
                />
              </div>

              <div style={{ marginBottom: "16px" }}>
                <label style={{ display: "block", fontSize: "12px", color: "var(--text-secondary)", marginBottom: "4px" }}>Category</label>
                <select
                  className="bb-input"
                  value={newSource.category}
                  onChange={(e) => setNewSource({ ...newSource, category: e.target.value })}
                >
                  <option value="competitor">Competitor Watch</option>
                  <option value="industry">Industry Trends</option>
                  <option value="consumer">Consumer Behavior</option>
                  <option value="pricing">Price & Deal Watch</option>
                </select>
              </div>

              {error && <div style={{ color: "#f87171", fontSize: "12px", marginBottom: "12px" }}>{error}</div>}

              <div style={{ display: "flex", justifySelf: "flex-end", gap: "8px" }}>
                <button type="button" onClick={() => setShowAddModal(false)} className="btn-secondary" style={{ fontSize: "13px" }}>
                  Cancel
                </button>
                <button type="submit" disabled={submitting} className="btn-primary" style={{ fontSize: "13px" }}>
                  {submitting ? "Adding..." : "Save Source"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {loading ? (
        <div style={{ textAlign: "center", padding: "60px 0", color: "var(--text-secondary)" }}>Loading sources...</div>
      ) : (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(320px, 1fr))", gap: "16px" }}>
          {sources.map((src) => (
            <div key={src.id} className="glass-card" style={{ padding: "20px" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "12px" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                  <Globe size={18} style={{ color: "var(--accent)" }} />
                  <div>
                    <h3 style={{ fontSize: "15px", fontWeight: 600, color: "var(--text)" }}>{src.name}</h3>
                    <span style={{ fontSize: "11px", color: "var(--text-dim)", textTransform: "uppercase" }}>{src.category}</span>
                  </div>
                </div>

                <button onClick={() => handleDeleteSource(src.id)} style={{ background: "none", border: "none", color: "var(--text-dim)", cursor: "pointer" }}>
                  <Trash2 size={15} />
                </button>
              </div>

              <div style={{ fontSize: "12px", color: "var(--text-secondary)", marginBottom: "14px", wordBreak: "break-all" }}>
                {src.url}
              </div>

              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", borderTop: "1px solid var(--border)", paddingTop: "12px", fontSize: "11px" }}>
                <span style={{ color: src.enabled ? "var(--green)" : "#f87171", display: "flex", alignItems: "center", gap: "4px", fontWeight: 600 }}>
                  {src.enabled ? <CheckCircle size={12} /> : <XCircle size={12} />}
                  {src.enabled ? "ACTIVE" : "DISABLED"}
                </span>

                <span style={{ color: "var(--text-dim)" }}>
                  Interval: Every {src.frequency_hours || 6}h
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
