"use client";

import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Activity,
  Sparkles,
  Search,
  CheckCircle2,
  AlertTriangle,
  Server,
  Zap,
  TrendingUp,
  Sliders,
  ShieldCheck,
  Bot,
  Command,
  FileText,
  RefreshCw,
} from "lucide-react";

export default function AdminDashboard() {
  const [activeTab, setActiveTab] = useState<"overview" | "brief" | "ai_ops" | "review_queue" | "flags">("overview");
  const [commandPaletteOpen, setCommandPaletteOpen] = useState(false);
  const [copilotOpen, setCopilotOpen] = useState(false);
  const [copilotQuery, setCopilotQuery] = useState("");
  const [copilotChat, setCopilotChat] = useState<Array<{ role: "user" | "assistant"; text: string }>>([
    {
      role: "assistant",
      text: "Hello Rohit. I am your Brand Battle Admin AI Copilot. Ask me anything about platform health, scraper status, CTR drops, or review items.",
    },
  ]);
  const [searchQuery, setSearchQuery] = useState("");

  // Keyboard shortcut Cmd+K / Ctrl+K for Command Palette
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        setCommandPaletteOpen((prev) => !prev);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  const handleCopilotSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!copilotQuery.trim()) return;

    const userText = copilotQuery;
    setCopilotChat((prev) => [...prev, { role: "user", text: userText }]);
    setCopilotQuery("");

    setTimeout(() => {
      let reply = "All 6 core AI subsystems (PKG, Matching, Search, Recs, Pricing, Notifications) are operating within SLO parameters.";
      const q = userText.toLowerCase();
      if (q.includes("ctr") || q.includes("recommendation")) {
        reply = "Recommendation CTR improved by +4.2% today following the hybrid graph model deployment. Highest uplift in Smartphones (+6.8%).";
      } else if (q.includes("scraper") || q.includes("fail") || q.includes("stale")) {
        reply = "2 marketplace scrapers (Ajio, Flipkart) experienced rate limiting between 03:00-04:15 UTC. Both have auto-recovered with 99.4% freshness.";
      } else if (q.includes("review") || q.includes("low") || q.includes("queue")) {
        reply = "There are 17 products with low completeness (<60% coverage) and 4 borderline matching candidates in the Review Queue.";
      }

      setCopilotChat((prev) => [...prev, { role: "assistant", text: reply }]);
    }, 600);
  };

  return (
    <div className="min-h-screen bg-[#050505] text-[#f4f4f5] font-sans antialiased pb-24">
      {/* Top Header */}
      <header className="sticky top-0 z-40 border-b border-[#27272a]/60 bg-[#050505]/80 backdrop-blur-xl px-8 py-4 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-[#f20ab0] to-purple-600 flex items-center justify-center font-bold text-white shadow-[0_0_20px_rgba(242,10,176,0.4)]">
            BB
          </div>
          <div>
            <h1 className="text-lg font-bold tracking-tight text-white flex items-center gap-2">
              Brand Battle Enterprise Command Center
              <span className="text-[0.65rem] px-2 py-0.5 bg-[#f20ab0]/10 border border-[#f20ab0]/30 text-[#f20ab0] font-semibold tracking-widest uppercase rounded-full">
                v8.0 Operational
              </span>
            </h1>
            <p className="text-xs text-[#a1a1aa]">Operational Control Center & Decision Intelligence Layer</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {/* Quick Command Palette Trigger */}
          <button
            onClick={() => setCommandPaletteOpen(true)}
            className="flex items-center gap-2 text-xs px-4 py-2 rounded-lg bg-[#18181b] border border-[#27272a] text-[#a1a1aa] hover:text-white hover:border-[#3f3f46] transition"
          >
            <Command className="w-3.5 h-3.5 text-[#f20ab0]" />
            <span>Command Palette...</span>
            <kbd className="text-[0.65rem] px-1.5 py-0.5 bg-[#27272a] text-[#a1a1aa] rounded font-mono">⌘K</kbd>
          </button>

          {/* AI Copilot Trigger */}
          <button
            onClick={() => setCopilotOpen((prev) => !prev)}
            className="flex items-center gap-2 text-xs px-4 py-2 rounded-lg bg-[#f20ab0] text-white font-medium hover:bg-[#d00896] transition shadow-[0_0_15px_rgba(242,10,176,0.3)]"
          >
            <Bot className="w-4 h-4" />
            <span>AI Copilot</span>
          </button>
        </div>
      </header>

      {/* Main Container */}
      <main className="max-w-[1600px] mx-auto px-8 mt-8">
        {/* Executive Morning Brief Card */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8 p-6 rounded-2xl bg-gradient-to-r from-[#18181b] via-[#121215] to-[#18181b] border border-[#27272a] shadow-2xl relative overflow-hidden"
        >
          <div className="absolute top-0 right-0 w-96 h-96 bg-[#f20ab0]/5 blur-[120px] rounded-full pointer-events-none" />
          <div className="flex items-center justify-between border-b border-[#27272a]/60 pb-4 mb-4">
            <div className="flex items-center gap-3">
              <Sparkles className="w-5 h-5 text-[#f20ab0]" />
              <h2 className="text-base font-bold tracking-tight text-white">Executive Morning Brief — 24h Operational Summary</h2>
            </div>
            <span className="text-xs text-[#71717a] font-mono">2026-08-02 • Generated by AI Intelligence Layer</span>
          </div>

          <div className="space-y-2 text-sm text-[#d4d4d8] leading-relaxed font-normal">
            <p className="font-semibold text-white">Good morning, Rohit. Here is what happened in the last 24 hours:</p>
            <ul className="grid grid-cols-1 md:grid-cols-2 gap-3 mt-3 text-xs text-[#a1a1aa]">
              <li className="flex items-start gap-2 bg-[#09090b] p-3 rounded-xl border border-[#27272a]/50">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                <span>Search success rate increased from 95.8% to 97.1% (Avg latency: 18.5ms).</span>
              </li>
              <li className="flex items-start gap-2 bg-[#09090b] p-3 rounded-xl border border-[#27272a]/50">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                <span>AI Matching resolved 14,382 new marketplace offers with 96.4% confidence.</span>
              </li>
              <li className="flex items-start gap-2 bg-[#09090b] p-3 rounded-xl border border-[#27272a]/50">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                <span>Users collectively saved an estimated ₹18.4 lakh through Price Intelligence.</span>
              </li>
              <li className="flex items-start gap-2 bg-[#09090b] p-3 rounded-xl border border-[#27272a]/50">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                <span>2 marketplace scrapers (Ajio, Flipkart) auto-recovered with 99.4% freshness.</span>
              </li>
            </ul>
          </div>
        </motion.div>

        {/* Navigation Tabs */}
        <div className="flex border-b border-[#27272a] gap-8 mb-8">
          {[
            { id: "overview", label: "Executive Overview", icon: Activity },
            { id: "ai_ops", label: "AI Operations Center", icon: Server },
            { id: "review_queue", label: "Unified Review Queue (17)", icon: Sliders },
            { id: "flags", label: "Feature Flag Center", icon: Zap },
          ].map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center gap-2 py-3 border-b-2 text-sm font-medium transition ${
                  isActive ? "border-[#f20ab0] text-white" : "border-transparent text-[#71717a] hover:text-[#a1a1aa]"
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? "text-[#f20ab0]" : "text-[#71717a]"}`} />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>

        {/* Tab 1: Executive Overview */}
        {activeTab === "overview" && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="p-5 rounded-2xl bg-[#09090b] border border-[#27272a]">
              <div className="text-xs font-semibold text-[#71717a] uppercase tracking-wider">Active Users (24h)</div>
              <div className="text-3xl font-extrabold text-white mt-2">14,250</div>
              <div className="text-xs text-emerald-400 mt-1">↑ +18.4% from last week</div>
            </div>

            <div className="p-5 rounded-2xl bg-[#09090b] border border-[#27272a]">
              <div className="text-xs font-semibold text-[#71717a] uppercase tracking-wider">Search Success Rate</div>
              <div className="text-3xl font-extrabold text-white mt-2">97.1%</div>
              <div className="text-xs text-emerald-400 mt-1">1.2% zero-result rate</div>
            </div>

            <div className="p-5 rounded-2xl bg-[#09090b] border border-[#27272a]">
              <div className="text-xs font-semibold text-[#71717a] uppercase tracking-wider">Recommendation CTR</div>
              <div className="text-3xl font-extrabold text-white mt-2">24.8%</div>
              <div className="text-xs text-[#f20ab0] mt-1">78.2% acceptance rate</div>
            </div>

            <div className="p-5 rounded-2xl bg-[#09090b] border border-[#27272a]">
              <div className="text-xs font-semibold text-[#71717a] uppercase tracking-wider">Happiness Index</div>
              <div className="text-3xl font-extrabold text-white mt-2">94.5%</div>
              <div className="text-xs text-emerald-400 mt-1">99.95% delivery success</div>
            </div>
          </div>
        )}

        {/* Tab 2: AI Operations Center */}
        {activeTab === "ai_ops" && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[
              { name: "Product Knowledge Graph", health: "Healthy", accuracy: "98.4%", latency: "4.2 ms" },
              { name: "AI Matching Engine", health: "Healthy", accuracy: "96.4%", latency: "12.0 ms" },
              { name: "Recommendation Engine", health: "Healthy", accuracy: "24.8% CTR", latency: "14.5 ms" },
              { name: "Search Platform", health: "Healthy", accuracy: "97.1%", latency: "18.5 ms" },
              { name: "Price Intelligence", health: "Healthy", accuracy: "94.2%", latency: "12.4 ms" },
              { name: "Notification Platform", health: "Healthy", accuracy: "94.5% Happiness", latency: "128.0 ms" },
            ].map((sub, idx) => (
              <div key={idx} className="p-6 rounded-2xl bg-[#09090b] border border-[#27272a]">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-sm font-bold text-white">{sub.name}</h3>
                  <span className="text-xs px-2.5 py-1 bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 font-semibold rounded-full">
                    {sub.health}
                  </span>
                </div>
                <div className="space-y-2 text-xs text-[#a1a1aa]">
                  <div className="flex justify-between">
                    <span>Performance / Accuracy:</span>
                    <span className="text-white font-medium">{sub.accuracy}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Latency (P95):</span>
                    <span className="text-white font-mono">{sub.latency}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Tab 3: Unified Review Queue */}
        {activeTab === "review_queue" && (
          <div className="space-y-4">
            {[
              { id: 1, type: "Matching Review", title: "Borderline Match: Samsung S26 Ultra vs S26 Edge", confidence: "64%" },
              { id: 2, type: "Product Merge", title: "Duplicate Canonical Candidate: iPhone 17 Pro Max 256GB", confidence: "88%" },
            ].map((item) => (
              <div key={item.id} className="p-5 rounded-2xl bg-[#09090b] border border-[#27272a] flex items-center justify-between">
                <div>
                  <span className="text-[0.65rem] uppercase tracking-wider px-2 py-0.5 bg-[#f20ab0]/10 text-[#f20ab0] border border-[#f20ab0]/30 rounded-full font-bold">
                    {item.type}
                  </span>
                  <h4 className="text-sm font-bold text-white mt-1">{item.title}</h4>
                  <p className="text-xs text-[#71717a]">Confidence: {item.confidence}</p>
                </div>
                <div className="flex gap-2">
                  <button className="text-xs px-4 py-2 rounded-lg bg-emerald-600 text-white font-medium hover:bg-emerald-500 transition">
                    Approve
                  </button>
                  <button className="text-xs px-4 py-2 rounded-lg bg-[#27272a] text-white hover:bg-[#3f3f46] transition">
                    Reject
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Tab 4: Feature Flags */}
        {activeTab === "flags" && (
          <div className="space-y-4">
            {[
              { key: "search_semantic_v2", name: "Semantic Vector Search v2", status: "Active (100%)" },
              { key: "recommendation_hybrid_graph", name: "Hybrid Graph Recommendation Model", status: "Active (100%)" },
              { key: "price_intelligence_forecast_v5", name: "Price Forecast Intelligence v5", status: "Active (100%)" },
              { key: "notification_daily_digest", name: "Daily AI Digest Generator", status: "Active (100%)" },
            ].map((flag) => (
              <div key={flag.key} className="p-5 rounded-2xl bg-[#09090b] border border-[#27272a] flex items-center justify-between">
                <div>
                  <h4 className="text-sm font-bold text-white">{flag.name}</h4>
                  <p className="text-xs font-mono text-[#71717a]">{flag.key}</p>
                </div>
                <span className="text-xs px-3 py-1 bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 font-semibold rounded-full">
                  {flag.status}
                </span>
              </div>
            ))}
          </div>
        )}
      </main>

      {/* Command Palette Modal */}
      <AnimatePresence>
        {commandPaletteOpen && (
          <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-start justify-center pt-28 px-4">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="w-full max-w-xl bg-[#09090b] border border-[#27272a] rounded-2xl p-4 shadow-2xl"
            >
              <div className="flex items-center gap-3 border-b border-[#27272a] pb-3">
                <Search className="w-5 h-5 text-[#71717a]" />
                <input
                  type="text"
                  placeholder="Type a command or search action (e.g. audit logs, matching...)"
                  className="w-full bg-transparent text-sm text-white placeholder-[#71717a] focus:outline-none"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  autoFocus
                />
              </div>

              <div className="mt-3 space-y-1 text-xs">
                {[
                  { title: "Open Product Operations Center", cat: "Navigation" },
                  { title: "View AI Matching Borderline Cases", cat: "Review Queue" },
                  { title: "Open Executive Morning Brief", cat: "Briefings" },
                  { title: "Audit Admin Actions & Logs", cat: "Compliance" },
                  { title: "Manage Feature Flags & Rollouts", cat: "Operations" },
                ]
                  .filter((c) => c.title.toLowerCase().includes(searchQuery.toLowerCase()))
                  .map((cmd, i) => (
                    <button
                      key={i}
                      onClick={() => setCommandPaletteOpen(false)}
                      className="w-full text-left p-2.5 rounded-lg hover:bg-[#18181b] flex items-center justify-between text-white transition"
                    >
                      <span>{cmd.title}</span>
                      <span className="text-[0.65rem] px-2 py-0.5 bg-[#27272a] text-[#a1a1aa] rounded">
                        {cmd.cat}
                      </span>
                    </button>
                  ))}
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* AI Copilot Drawer */}
      <AnimatePresence>
        {copilotOpen && (
          <motion.div
            initial={{ x: 400 }}
            animate={{ x: 0 }}
            exit={{ x: 400 }}
            className="fixed top-0 right-0 w-96 h-full bg-[#09090b] border-l border-[#27272a] z-50 flex flex-col p-6 shadow-2xl"
          >
            <div className="flex items-center justify-between border-b border-[#27272a] pb-4 mb-4">
              <div className="flex items-center gap-2">
                <Bot className="w-5 h-5 text-[#f20ab0]" />
                <h3 className="text-sm font-bold text-white">Admin AI Copilot</h3>
              </div>
              <button onClick={() => setCopilotOpen(false)} className="text-xs text-[#71717a] hover:text-white">
                ✕
              </button>
            </div>

            <div className="flex-1 overflow-y-auto space-y-4 text-xs pr-1">
              {copilotChat.map((msg, i) => (
                <div
                  key={i}
                  className={`p-3 rounded-xl ${
                    msg.role === "user" ? "bg-[#f20ab0]/10 text-white ml-6 border border-[#f20ab0]/30" : "bg-[#18181b] text-[#d4d4d8] border border-[#27272a]"
                  }`}
                >
                  {msg.text}
                </div>
              ))}
            </div>

            <form onSubmit={handleCopilotSubmit} className="mt-4 pt-3 border-t border-[#27272a] flex gap-2">
              <input
                type="text"
                placeholder="Ask Copilot a question..."
                className="flex-1 bg-[#18181b] border border-[#27272a] rounded-lg px-3 py-2 text-xs text-white placeholder-[#71717a] focus:outline-none"
                value={copilotQuery}
                onChange={(e) => setCopilotQuery(e.target.value)}
              />
              <button type="submit" className="px-3 py-2 bg-[#f20ab0] text-white rounded-lg text-xs font-semibold">
                Send
              </button>
            </form>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
