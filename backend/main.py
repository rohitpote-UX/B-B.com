"""
Brand Battle — FastAPI Application
AI-powered product comparison and deal discovery platform.

Run: uvicorn main:app --reload --port 8000
Docs: http://localhost:8000/docs
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time

from config import settings
from database import init_db, check_db_health
from redis_client import is_redis_healthy
from middleware_security import SecurityHeadersMiddleware, RedisRateLimiterMiddleware
from logging_config import setup_logging, logger

# Initialize structured logging
setup_logging()


# ─── Lifespan ────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup
    logger.info(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION} [{settings.ENV}]")
    init_db()
    logger.info("✅ Database initialized")

    # Auto-seed in debug mode
    if settings.DEBUG:
        try:
            from seed_data import seed_database
            seed_database()
        except Exception as e:
            logger.warning(f"⚠️  Seed skipped: {e}")

    yield

    # Shutdown
    logger.info("👋 Shutting down application workers")


# ─── App ─────────────────────────────────────────────────────────────

app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "AI-powered product comparison and deal discovery platform. "
        "Compare products, find the best deals, track prices, and get "
        "personalized recommendations across Amazon, Flipkart, and more."
    ),
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ─── Middlewares ──────────────────────────────────────────────────────

# GZip compression for responses >= 1000 bytes
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Trusted Host Security Header
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.allowed_hosts_list
)

# Custom Security Headers
app.add_middleware(SecurityHeadersMiddleware)

# Redis Rate Limiting
app.add_middleware(RedisRateLimiterMiddleware)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Request timing middleware ───────────────────────────────────────

@app.middleware("http")
async def add_process_time(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.4f}"
    return response


# ─── Register Routers ───────────────────────────────────────────────

from routers.auth import router as auth_router
from routers.products import router as products_router
from routers.compare import router as compare_router
from routers.ai import router as ai_router
from routers.deals import router as deals_router
from routers.alerts import router as alerts_router
from routers.alerts import notifications_router
from routers.admin import router as admin_router
from routers.brands import router as brands_router
from routers.pipeline import router as pipeline_router
from routers.knowledge_graph import router as kg_router
from recommendation_engine import recommendation_router
from search_platform import search_router
from price_intelligence import price_intelligence_router
from notification_platform import notification_router
from analytics_platform import analytics_router
from admin_console import admin_console_router
from comparison_workspace import comparison_workspace_router
from seo_platform import seo_router
from affiliate_platform import affiliate_router
from verification_platform import verification_router

app.include_router(auth_router)
app.include_router(products_router)
app.include_router(compare_router)
app.include_router(ai_router)
app.include_router(deals_router)
app.include_router(alerts_router)
app.include_router(notifications_router)
app.include_router(admin_router)
app.include_router(brands_router)
app.include_router(pipeline_router)
app.include_router(kg_router)
app.include_router(recommendation_router)
app.include_router(search_router)
app.include_router(price_intelligence_router)
app.include_router(notification_router)
app.include_router(analytics_router)
app.include_router(admin_console_router)
app.include_router(comparison_workspace_router)
app.include_router(seo_router)
app.include_router(affiliate_router)
app.include_router(verification_router)


# ─── Root & Health Endpoints ─────────────────────────────────────────

@app.get("/", tags=["Root"])
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENV,
        "status": "running",
        "docs": "/docs",
        "description": "AI-powered product comparison & deal discovery platform",
    }


@app.get("/health", tags=["Root"])
async def health_check():
    """Liveness probe detailing core subsystem status."""
    db_ok = check_db_health()
    redis_ok = is_redis_healthy()
    status_str = "healthy" if (db_ok and redis_ok) else "degraded"
    
    return {
        "status": status_str,
        "version": settings.APP_VERSION,
        "environment": settings.ENV,
        "database": "connected" if db_ok else "unreachable",
        "redis_cache": "connected" if redis_ok else "disabled",
    }


@app.get("/ready", tags=["Root"])
async def readiness_check():
    """Readiness probe for Kubernetes / Container Orchestrators."""
    if not check_db_health():
        return JSONResponse(status_code=503, content={"status": "not_ready", "reason": "database_unavailable"})
    return {"status": "ready"}


@app.get("/api/stats", tags=["Root"])
async def get_stats():
    """Public-facing platform statistics."""
    from sqlalchemy import func
    from database import SessionLocal
    from models import Product, Brand, Deal, Comparison, User

    db = SessionLocal()
    try:
        return {
            "total_products": db.query(func.count(Product.id)).filter(Product.is_active == True).scalar() or 0,
            "total_brands": db.query(func.count(Brand.id)).scalar() or 0,
            "active_deals": db.query(func.count(Deal.id)).filter(Deal.status == "active").scalar() or 0,
            "total_comparisons": db.query(func.count(Comparison.id)).scalar() or 0,
            "total_users": db.query(func.count(User.id)).scalar() or 0,
            "platforms_tracked": 7,
        }
    finally:
        db.close()


# ─── Error Handlers ──────────────────────────────────────────────────

@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Resource not found", "path": str(request.url)},
    )


@app.exception_handler(500)
async def server_error_handler(request: Request, exc):
    logger.error(f"Internal server error handling request {request.url}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )
