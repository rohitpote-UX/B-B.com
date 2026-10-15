# B&B — BrandBattle Intelligence Agent

> **Discover the signal. Verify the evidence. Make the move.**

B&B Intelligence is an autonomous, internal AI market intelligence agent and human-in-the-loop content engine designed exclusively for **BrandBattle** (`https://brandbattle.in`).

---

## 🌟 Key Architecture & Capabilities

1. **Zero Impact on Live Production (`https://brandbattle.in`)**:
   - Built as an isolated standalone Next.js 15 application in `bb-intelligence/` directory.
   - Guaranteed zero changes or side-effects to existing production code.

2. **Ingestion & Collector Engine**:
   - Automated RSS/Atom feed collection with SSRF safety guards (`validateOutboundUrl`, `safeFetch`).
   - Deduplication and SHA-256 content fingerprinting (`raw_hash` vs `normalized_hash`).

3. **Evidence Vault & Ground-Truth Verification**:
   - State machine verification rating (`VERIFIED`, `UNVERIFIED`, `NEEDS_VERIFICATION`, `CONTRADICTED`).
   - Ground-truth citation links, direct quotes, and corroboration scoring.

4. **Explainable 4-Pillar Scoring Model**:
   - Scores every signal across: **Brand Impact** (35%), **Market Reach** (25%), **Customer Relevance** (25%), and **Strategic Urgency** (15%).

5. **Human-in-the-Loop Approval Queue & Safety Gates**:
   - Mandatory human approval for all external posts.
   - Hard safety gates block unverified or rejected content from publication.
   - Full immutable audit logging (`bb_audit_logs`).

6. **Dual Database Architecture**:
   - Connects seamlessly to **Neon Serverless Postgres** via `@neondatabase/serverless` when `DATABASE_URL` is set.
   - Falls back gracefully to an in-memory SQL driver for zero-config local development.

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Node.js 18+ installed

### 2. Environment Setup
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Default team password: `brandbattle2026!`

### 3. Start Development Server
```bash
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) in your browser. Log in with the team password.

### 4. Run Automated Test Suite
```bash
npx tsx test-runner.mjs
```

### 5. Build for Production
```bash
npm run build
```

---

## 📖 Operator Runbook

1. **Log in**: Enter team password on landing page.
2. **Collect Signals**: Click **"Run Intelligence Collector"** on the Overview Dashboard to fetch live RSS feeds.
3. **Review Signals**: Browse raw normalized articles in **Research Feed**.
4. **Evaluate Findings**: Inspect strategic opportunities in **Opportunities**. Click **"Generate X Post"** or **"Generate IG Brief"**.
5. **Verify Citations**: Check ground-truth source citations in **Evidence Review**.
6. **Approve Content**: Go to **Approval Queue**. Human operators must review and authorize or reject drafts before publication.
7. **Audit Trail**: Check system health and action history in **Settings & Audit Logs**.

---

*BrandBattle Internal Intelligence Agent — v1.0.0*
