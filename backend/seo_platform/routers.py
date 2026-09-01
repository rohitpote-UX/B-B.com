"""
Brand Battle — Enterprise SEO Platform REST API Layer
FastAPI router mounted at /api/seo/* providing metadata evaluation, sitemaps, robots.txt, and quality validation.
"""

from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, Response, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from seo_platform.services import seo_platform_service
from seo_platform.sitemap_service import dynamic_sitemap_service
from seo_platform.robots_service import robots_service
from seo_platform.schema_validator import automated_seo_quality_validator
from seo_platform.health_monitor import seo_health_monitor
from seo_platform.config import seo_config
from seo_platform.schemas import SeoEvaluateRequestSchema

router = APIRouter(prefix="/api/seo", tags=["SEO Platform"])


@router.post("/evaluate")
async def evaluate_seo_page(
    payload: SeoEvaluateRequestSchema,
    db: Session = Depends(get_db),
):
    """Generate complete SEO metadata, JSON-LD, FAQs, intro/outro, and canonical URL (<20ms target)."""
    res = seo_platform_service.evaluate_comparison_seo(
        db=db, p1_id=payload.product1_id, p2_id=payload.product2_id
    )
    return {
        "success": True,
        "message": "SEO metadata generated successfully",
        "data": res.model_dump(),
    }


@router.get("/sitemap.xml")
async def get_sitemap():
    """Generate dynamic XML sitemap."""
    urls = [
        f"{seo_config.domain}/",
        f"{seo_config.domain}/compare",
        f"{seo_config.domain}/compare/iphone-17-pro-max-vs-samsung-galaxy-s26-ultra",
        f"{seo_config.domain}/compare/macbook-pro-m5-vs-dell-xps-15",
        f"{seo_config.domain}/deals",
        f"{seo_config.domain}/discover",
    ]
    xml_data = dynamic_sitemap_service.generate_sitemap_xml(urls)
    return Response(content=xml_data, media_type="application/xml")


@router.get("/robots.txt")
async def get_robots():
    """Generate robots.txt crawl directives."""
    robots_data = robots_service.generate_robots_txt()
    return Response(content=robots_data, media_type="text/plain")


@router.post("/validate")
async def validate_seo(
    title: str,
    meta_description: str,
    canonical_url: str,
):
    """20. Automated SEO Quality Validator endpoint."""
    res = automated_seo_quality_validator.validate_page_seo(
        title=title,
        meta_description=meta_description,
        canonical_url=canonical_url,
        json_ld={"@context": "https://schema.org"},
    )
    return {
        "success": True,
        "message": "SEO validation completed",
        "data": res,
    }


@router.get("/audit")
async def audit_seo_health(db: Session = Depends(get_db)):
    """Operational health monitor calculating overall SEO Quality Score and thin content metrics."""
    audit_data = seo_health_monitor.run_full_seo_audit(db)
    return {
        "success": True,
        "message": "SEO health audit completed",
        "data": audit_data,
    }


@router.get("/health")
async def seo_health():
    """Health check endpoint."""
    return {
        "success": True,
        "message": "Enterprise SEO Comparison Publishing Platform operational",
        "data": {
            "status": "healthy",
            "version": "v10.0-enterprise-seo-publishing-platform",
        },
    }
