"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

export default function LoginPage() {
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const router = useRouter();

  useEffect(() => {
    // Check if already logged in
    fetch("/api/intelligence/overview")
      .then((r) => { if (r.ok) router.replace("/dashboard"); })
      .catch(() => {});
  }, [router]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const res = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ password }),
      });
      const data = await res.json();
      if (!res.ok) {
        setError(data.error || "Authentication failed.");
        return;
      }
      router.replace("/dashboard");
    } catch {
      setError("Connection error. Is the server running?");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: "var(--bg)",
        padding: "24px",
        position: "relative",
        overflow: "hidden",
      }}
    >
      {/* Background glow */}
      <div
        style={{
          position: "absolute",
          top: "30%",
          left: "50%",
          transform: "translate(-50%, -50%)",
          width: "600px",
          height: "600px",
          background: "radial-gradient(circle, rgba(242,10,176,0.08) 0%, transparent 70%)",
          pointerEvents: "none",
        }}
      />

      <div
        className="glass-card"
        style={{
          width: "100%",
          maxWidth: "420px",
          padding: "40px",
          position: "relative",
          zIndex: 1,
        }}
      >
        {/* Logo */}
        <div style={{ textAlign: "center", marginBottom: "32px" }}>
          <div
            style={{
              display: "inline-flex",
              alignItems: "center",
              justifyContent: "center",
              width: "56px",
              height: "56px",
              borderRadius: "16px",
              background: "linear-gradient(135deg, #f20ab0, #9b30d0)",
              fontFamily: "Outfit, sans-serif",
              fontWeight: 800,
              fontSize: "20px",
              color: "white",
              marginBottom: "16px",
              boxShadow: "0 0 30px rgba(242,10,176,0.4)",
            }}
          >
            B&B
          </div>
          <h1
            style={{
              fontFamily: "Outfit, sans-serif",
              fontSize: "24px",
              fontWeight: 700,
              color: "var(--text)",
              marginBottom: "6px",
            }}
          >
            BrandBattle Intelligence
          </h1>
          <p style={{ fontSize: "13px", color: "var(--text-secondary)", lineHeight: "1.5" }}>
            Discover the signal. Verify the evidence. Make the move.
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: "16px" }}>
            <label
              htmlFor="password"
              style={{
                display: "block",
                fontSize: "12px",
                fontWeight: 600,
                color: "var(--text-secondary)",
                marginBottom: "8px",
                letterSpacing: "0.05em",
                textTransform: "uppercase",
              }}
            >
              Team Access Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter team password"
              className="bb-input"
              required
              autoFocus
              autoComplete="current-password"
            />
          </div>

          {error && (
            <div
              style={{
                padding: "10px 14px",
                background: "rgba(248,113,113,0.1)",
                border: "1px solid rgba(248,113,113,0.3)",
                borderRadius: "8px",
                fontSize: "13px",
                color: "#f87171",
                marginBottom: "16px",
              }}
            >
              {error}
            </div>
          )}

          <button
            type="submit"
            className="btn-primary"
            disabled={loading}
            style={{ width: "100%", justifyContent: "center", padding: "12px 18px", fontSize: "14px" }}
          >
            {loading ? "Authenticating..." : "Access Intelligence Platform →"}
          </button>
        </form>

        <p
          style={{
            textAlign: "center",
            fontSize: "11px",
            color: "var(--text-dim)",
            marginTop: "24px",
            lineHeight: "1.6",
          }}
        >
          Internal use only. Unauthorized access is prohibited.
          <br />
          All actions are logged.
        </p>
      </div>
    </div>
  );
}
