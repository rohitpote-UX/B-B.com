"use client";

import { useState, useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";
import Link from "next/link";
import {
  LayoutDashboard,
  Newspaper,
  Database,
  ShieldCheck,
  Lightbulb,
  PenTool,
  CheckSquare,
  Settings,
  LogOut,
  Zap,
  ChevronRight,
} from "lucide-react";

const NAV_ITEMS = [
  { href: "/dashboard", label: "Overview", icon: LayoutDashboard, exact: true },
  { href: "/dashboard/research", label: "Research Feed", icon: Newspaper },
  { href: "/dashboard/sources", label: "Source Registry", icon: Database },
  { href: "/dashboard/evidence", label: "Evidence Review", icon: ShieldCheck },
  { href: "/dashboard/opportunities", label: "Opportunities", icon: Lightbulb },
  { href: "/dashboard/content", label: "Content Studio", icon: PenTool },
  { href: "/dashboard/approvals", label: "Approval Queue", icon: CheckSquare },
  { href: "/dashboard/settings", label: "Settings", icon: Settings },
];

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [stats, setStats] = useState({ pending_approvals: 0, active_findings: 0 });
  const [loggingOut, setLoggingOut] = useState(false);

  useEffect(() => {
    fetch("/api/intelligence/overview")
      .then((r) => r.json())
      .then((d) => {
        if (d.stats) setStats(d.stats);
      })
      .catch(() => {});
  }, []);

  async function handleLogout() {
    setLoggingOut(true);
    await fetch("/api/auth/logout", { method: "POST" });
    router.replace("/");
  }

  function isActive(item: (typeof NAV_ITEMS)[0]) {
    if (item.exact) return pathname === item.href;
    return pathname.startsWith(item.href);
  }

  return (
    <div style={{ display: "flex", minHeight: "100vh", background: "var(--bg)" }}>
      {/* Sidebar */}
      <aside
        style={{
          width: "240px",
          flexShrink: 0,
          borderRight: "1px solid var(--border)",
          background: "var(--bg-elevated)",
          display: "flex",
          flexDirection: "column",
          position: "sticky",
          top: 0,
          height: "100vh",
          overflow: "hidden",
        }}
      >
        {/* Logo */}
        <div
          style={{
            padding: "20px 20px 16px",
            borderBottom: "1px solid var(--border)",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
            <div
              style={{
                width: "36px",
                height: "36px",
                borderRadius: "10px",
                background: "linear-gradient(135deg, #f20ab0, #9b30d0)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontFamily: "Outfit, sans-serif",
                fontWeight: 800,
                fontSize: "13px",
                color: "white",
                boxShadow: "0 0 16px rgba(242,10,176,0.4)",
                flexShrink: 0,
              }}
            >
              B&B
            </div>
            <div>
              <div
                style={{
                  fontFamily: "Outfit, sans-serif",
                  fontWeight: 700,
                  fontSize: "14px",
                  color: "var(--text)",
                  letterSpacing: "-0.02em",
                }}
              >
                Intelligence
              </div>
              <div style={{ fontSize: "10px", color: "var(--text-secondary)", letterSpacing: "0.04em" }}>
                BrandBattle
              </div>
            </div>
          </div>

          {/* Live indicator */}
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "6px",
              marginTop: "12px",
              padding: "5px 10px",
              background: "rgba(0,214,143,0.08)",
              border: "1px solid rgba(0,214,143,0.2)",
              borderRadius: "6px",
              width: "fit-content",
            }}
          >
            <span
              style={{
                width: "6px",
                height: "6px",
                borderRadius: "50%",
                background: "var(--green)",
                boxShadow: "0 0 6px #00d68f",
                animation: "pulse-subtle 2s infinite",
                display: "inline-block",
              }}
            />
            <span style={{ fontSize: "10px", fontWeight: 700, color: "var(--green)", letterSpacing: "0.05em" }}>
              SYSTEM LIVE
            </span>
          </div>
        </div>

        {/* Navigation */}
        <nav style={{ padding: "12px 12px", flex: 1, overflow: "auto" }}>
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const active = isActive(item);
            const badge =
              item.href === "/dashboard/approvals"
                ? stats.pending_approvals
                : item.href === "/dashboard/opportunities"
                ? stats.active_findings
                : 0;

            return (
              <Link
                key={item.href}
                href={item.href}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "10px",
                  padding: "9px 10px",
                  borderRadius: "8px",
                  marginBottom: "2px",
                  background: active ? "rgba(242,10,176,0.12)" : "transparent",
                  border: active ? "1px solid rgba(242,10,176,0.25)" : "1px solid transparent",
                  color: active ? "#f20ab0" : "var(--text-secondary)",
                  fontSize: "13px",
                  fontWeight: active ? 600 : 400,
                  textDecoration: "none",
                  transition: "all 0.15s",
                  position: "relative",
                }}
                onMouseEnter={(e) => {
                  if (!active) {
                    (e.currentTarget as HTMLAnchorElement).style.background = "rgba(255,255,255,0.04)";
                    (e.currentTarget as HTMLAnchorElement).style.color = "var(--text)";
                  }
                }}
                onMouseLeave={(e) => {
                  if (!active) {
                    (e.currentTarget as HTMLAnchorElement).style.background = "transparent";
                    (e.currentTarget as HTMLAnchorElement).style.color = "var(--text-secondary)";
                  }
                }}
              >
                <Icon size={15} />
                <span style={{ flex: 1 }}>{item.label}</span>
                {badge > 0 && (
                  <span
                    style={{
                      background: "var(--accent)",
                      color: "white",
                      fontSize: "10px",
                      fontWeight: 700,
                      padding: "1px 6px",
                      borderRadius: "10px",
                      lineHeight: "16px",
                    }}
                  >
                    {badge}
                  </span>
                )}
                {active && <ChevronRight size={12} style={{ opacity: 0.6 }} />}
              </Link>
            );
          })}
        </nav>

        {/* Footer */}
        <div style={{ padding: "12px", borderTop: "1px solid var(--border)" }}>
          <button
            onClick={handleLogout}
            disabled={loggingOut}
            className="btn-secondary"
            style={{ width: "100%", justifyContent: "center", fontSize: "12px" }}
          >
            <LogOut size={13} />
            {loggingOut ? "Logging out..." : "Sign Out"}
          </button>
          <p
            style={{
              textAlign: "center",
              fontSize: "10px",
              color: "var(--text-dim)",
              marginTop: "8px",
            }}
          >
            v1.0.0 · Internal Only
          </p>
        </div>
      </aside>

      {/* Main content */}
      <main style={{ flex: 1, overflow: "auto", minWidth: 0 }}>
        {/* Top bar */}
        <div
          style={{
            position: "sticky",
            top: 0,
            zIndex: 20,
            background: "rgba(3,3,5,0.85)",
            backdropFilter: "blur(16px)",
            borderBottom: "1px solid var(--border)",
            padding: "12px 28px",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "12px", color: "var(--text-muted)" }}>
            <Zap size={12} style={{ color: "var(--accent)" }} />
            <span style={{ color: "var(--text-secondary)" }}>B&B Intelligence</span>
            <span style={{ color: "var(--text-dim)" }}>
              · {NAV_ITEMS.find((n) => isActive(n))?.label || "Dashboard"}
            </span>
          </div>
          <div style={{ display: "flex", gap: "8px" }}>
            {stats.pending_approvals > 0 && (
              <Link href="/dashboard/approvals" style={{ textDecoration: "none" }}>
                <span className="badge badge-needs-review">
                  {stats.pending_approvals} awaiting approval
                </span>
              </Link>
            )}
          </div>
        </div>

        {/* Page content */}
        <div style={{ padding: "28px" }}>{children}</div>
      </main>
    </div>
  );
}
