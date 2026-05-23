# 🥊 Brand Battle (BandB)

**An AI-powered product comparison and deal discovery platform.**

Users search for products (phones, laptops, headphones, etc.), compare them side-by-side, find the best deals across multiple e-commerce platforms (Amazon, Flipkart, Myntra, Croma, etc.), set price alerts, and get AI-powered buying recommendations — all in one place.

---

## 🧠 The Core Idea

Think of it like this:

> A user wants to buy wireless earbuds. Instead of opening 5 different shopping sites, comparing prices manually, and reading dozens of reviews — they come to **Brand Battle**, search "wireless earbuds under ₹5000", and instantly get:
>
> - A list of matching products with prices from every platform
> - A side-by-side comparison table (battery, sound quality, etc.)
> - An AI summary: _"The Sony WF-C500 offers the best value for money with superior battery life, while the boAt Airdopes 441 is the budget pick"_
> - Active deals & coupon codes
> - A price history chart showing the best time to buy

---

## 📐 How the App Works (High-Level Flow)

```
┌─────────────┐     ┌──────────────┐     ┌──────────────────┐
│   Frontend   │────▶│   Backend    │────▶│    Database       │
│  (React +    │◀────│  (FastAPI +  │◀────│  (SQLite/Postgres)│
│   Vite)      │     │   Python)    │     └──────────────────┘
└─────────────┘     └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │  AI Engine   │
                    │  (OpenAI)    │
                    └──────────────┘
```

### User Journey

1. **Landing Page** → User sees featured products, trending comparisons, and top deals
2. **Search / Discover** → User searches for a product or browses categories
3. **Product Detail** → Shows specs, reviews, prices across platforms, price history
4. **Compare** → Pick 2-5 products to compare side-by-side (specs, prices, ratings)
5. **AI Advisor** → Ask the AI: _"Best phone under ₹20k for gaming?"_ — it recommends products with reasoning
6. **Deals Page** → Browse active deals, filter by category/platform, see if a discount is genuine or fake
7. **Price Alerts** → Set a target price on a product; get notified when it drops
8. **Profile** → View saved comparisons, active alerts, search history

---

## 🗂️ Project Structure

```
BandB/
├── frontend/              # React + Vite (runs on port 5173)
│   └── src/
│       ├── pages/         # All UI pages (Landing, Search, Compare, Deals, AI Advisor, etc.)
│       ├── components/    # Shared components (Navbar, Footer, MobileNav)
│       └── data/          # Static/mock data files
│
├── backend/               # Python FastAPI (runs on port 8000)
│   ├── main.py            # App entry point, CORS, router registration
│   ├── config.py          # App settings (DB URL, JWT secret, API keys)
│   ├── database.py        # SQLAlchemy DB connection setup
│   ├── models.py          # All 14+ database tables (see below)
│   ├── schemas.py         # Pydantic request/response models for every endpoint
│   ├── auth.py            # JWT token creation & password hashing
│   ├── seed_data.py       # Auto-seeds demo data in debug mode
│   ├── requirements.txt   # Python dependencies
│   ├── .env.example       # Environment variable template
│   └── routers/           # API route handlers (one file per feature)
│       ├── auth.py        # Signup, login, profile, password reset
│       ├── products.py    # CRUD, search, filters, price history
│       ├── compare.py     # Create/view comparisons, voting
│       ├── ai.py          # AI recommendations, summaries, cart optimizer
│       ├── deals.py       # Browse/filter deals
│       ├── alerts.py      # Price alerts + notifications
│       ├── brands.py      # Brand listing & details
│       └── admin.py       # Admin dashboard, analytics, user/product management
│
└── README.md              # ← You are here
```

---

## 🗄️ Database Tables (What Data We Store)

| Table | Purpose |
|---|---|
| **users** | Registered users (email, password hash, role, preferences) |
| **brands** | Brand profiles (Apple, Samsung, etc.) with trust scores |
| **categories** | Product categories with parent-child hierarchy |
| **products** | Every product with specs, images, tags, AI summary, best price |
| **prices** | Current price of each product on each platform |
| **price_history** | Historical price records (for price charts) |
| **reviews** | User/platform reviews with sentiment analysis scores |
| **comparisons** | Saved product comparisons with AI winner & feature scores |
| **saved_comparisons** | Which users saved which comparisons |
| **votes** | Community votes on comparison winners |
| **deals** | Active/expired deals (with fake-discount detection) |
| **price_alerts** | User-set target prices (triggers notifications when hit) |
| **notifications** | In-app notifications (price drops, new deals, etc.) |
| **affiliate_links** | Monetization — affiliate URLs with click/conversion tracking |
| **search_history** | What users searched (for analytics & AI personalization) |
| **analytics_events** | Page views, clicks, and other behavioral events |

---

## 🔌 API Endpoints (What the Backend Exposes)

All endpoints are documented at `http://localhost:8000/docs` (Swagger UI) when the server is running.

### Auth (`/api/auth/...`)
- `POST /signup` — Register a new user
- `POST /login` — Get a JWT access token
- `GET /me` — Get current user profile
- `PUT /me` — Update profile & preferences

### Products (`/api/products/...`)
- `GET /` — List products (paginated, with filters)
- `GET /search?q=...` — Full-text product search
- `GET /{id}` — Product detail (with brand, category)
- `GET /{id}/prices` — All current prices across platforms
- `GET /{id}/price-history` — Historical price data
- `GET /{id}/reviews` — Reviews with sentiment scores

### Compare (`/api/compare/...`)
- `POST /` — Create a new comparison (2-5 product IDs)
- `GET /{slug}` — Get full comparison detail
- `GET /trending` — Trending comparisons
- `POST /vote` — Vote for a winner in a comparison

### AI (`/api/ai/...`)
- `POST /recommend` — Ask the AI for product recommendations (with budget, purpose)
- `POST /summarize` — Get an AI summary for a set of products
- `POST /cart-optimize` — Find the cheapest platform for each item in your cart

### Deals (`/api/deals/...`)
- `GET /` — List active deals (filter by category, platform, discount %)
- `GET /{id}` — Deal detail

### Alerts (`/api/alerts/...`)
- `POST /` — Create a price alert
- `GET /` — List your active alerts
- `DELETE /{id}` — Remove an alert

### Notifications (`/api/notifications/...`)
- `GET /` — List your notifications
- `PUT /{id}/read` — Mark as read

### Admin (`/api/admin/...`)
- `GET /analytics` — Dashboard stats
- User & product management endpoints

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React (JSX) + Vite |
| **Backend** | Python 3.10+ with FastAPI |
| **Database** | SQLite (dev) / PostgreSQL (prod) |
| **ORM** | SQLAlchemy |
| **Auth** | JWT (JSON Web Tokens) with bcrypt hashing |
| **AI** | OpenAI API (optional — mocks if key not set) |
| **Validation** | Pydantic v2 schemas |
| **API Docs** | Auto-generated Swagger at `/docs` |

---

## 🚀 How to Run Locally

### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate        # On Windows
# source venv/bin/activate   # On Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
copy .env.example .env       # Then edit .env with your settings

# Start the server
uvicorn main:app --reload --port 8000
```

The API will be live at `http://localhost:8000` and docs at `http://localhost:8000/docs`.

In debug mode (`DEBUG=true`), the database auto-seeds with sample products, brands, deals, and users on first run.

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

The frontend will be live at `http://localhost:5173`.

---

## 🔑 Environment Variables

| Variable | Description | Default |
|---|---|---|
| `DATABASE_URL` | PostgreSQL connection string | `sqlite:///./brandbattle.db` |
| `SECRET_KEY` | JWT signing secret (change in prod!) | dev key |
| `OPENAI_API_KEY` | OpenAI API key for AI features | empty (uses mock) |
| `REDIS_URL` | Redis URL for caching (optional) | `redis://localhost:6379/0` |
| `DEBUG` | Enable debug mode & auto-seeding | `true` |
| `CORS_ORIGINS` | Allowed frontend origins | `http://localhost:5173,http://localhost:3000` |

---

## 💡 Key Concepts for Backend Developers

1. **Multi-Platform Pricing** — Each product can have prices from 7+ platforms (Amazon, Flipkart, etc.). The system tracks which platform has the best deal right now.

2. **AI Layer** — The AI router (`routers/ai.py`) handles recommendation queries, product summaries, and cart optimization. If `OPENAI_API_KEY` is not set, it falls back to mock/rule-based responses.

3. **Fake Discount Detection** — Deals have an `is_fake_discount` flag and a `real_market_price` field. The system compares the "original price" shown by sellers against actual historical pricing.

4. **Price History** — Every time prices are fetched, a snapshot goes into `price_history`. This powers the price trend charts on the frontend.

5. **Comparison Voting** — Users can vote for which product they think wins in a comparison. Votes are unique per user per comparison.

6. **JWT Auth** — All protected routes require a `Bearer` token in the `Authorization` header. Tokens expire after 24 hours by default.

7. **Seed Data** — When `DEBUG=true`, running the server auto-populates the DB with realistic sample data (products, brands, deals, users) so the frontend works out of the box.

8. **Affiliate Monetization** — Products can have affiliate links per platform with click/conversion tracking and revenue reporting.

---

## 📝 What's Left to Build / Improve

- [ ] Real-time price scraping (currently uses seeded/manual data)
- [ ] Email/push notification delivery for price alerts
- [ ] User authentication on the frontend (login/signup pages exist but need API wiring)
- [ ] Admin panel UI
- [ ] Production deployment (Docker, CI/CD)
- [ ] Rate limiting and caching (Redis integration)
- [ ] Full-text search with Elasticsearch (currently basic SQL LIKE queries)

---

> **Questions?** Check the auto-generated API docs at `/docs` after starting the backend, or read through `models.py` and `schemas.py` for the complete data structure.
