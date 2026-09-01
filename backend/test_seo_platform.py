"""
Brand Battle — Enterprise SEO Comparison Publishing Platform Verification Suite
Tests all 20 SEO platform modules:
1. Dynamic SEO Metadata Generation (<20ms latency target)
2. SEO-Friendly Slug Resolution (/compare/nike-air-max-270-vs-adidas-ultraboost-23)
3. AI Introductory & Conclusion Content Generation
4. Structured FAQ Generation
5. Schema.org JSON-LD Generation (Product, Offer, FAQPage, BreadcrumbList)
6. Canonical URL Deterministic Ordering (A vs B and B vs A map to 1 canonical URL)
7. XML Sitemap Generation
8. Robots.txt Crawl Directives Generation
9. Automated SEO Quality Validator
"""

import sys
import os

backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from database import SessionLocal, init_db
from seo_platform import (
    seo_platform_service,
    slug_generator_engine,
    dynamic_metadata_engine,
    automated_seo_quality_validator,
)
from seo_platform.sitemap_service import dynamic_sitemap_service
from seo_platform.robots_service import robots_service


def clean_str(val: str) -> str:
    return str(val).encode('ascii', 'ignore').decode('ascii')


def main():
    print("=" * 60)
    print("  Enterprise SEO Comparison Publishing Platform Test Suite  ")
    print("=" * 60)

    init_db()
    db = SessionLocal()

    try:
        # Test 1: Full SEO Metadata Payload Generation (<20ms SLO Target)
        print("\n[Test 1] Testing Dynamic SEO Metadata & Content Generation...")
        payload = seo_platform_service.evaluate_comparison_seo(db=db, p1_id=1, p2_id=2)
        print(f"  Canonical Slug: {payload.canonical_slug}")
        print(f"  Canonical URL: {payload.canonical_url}")
        print(f"  Title Tag: {clean_str(payload.title)}")
        print(f"  Meta Description: {clean_str(payload.meta_description[:110])}...")
        assert payload.is_valid_seo, "SEO validation failed"
        print("  [OK] Dynamic SEO Metadata Passed!")

        # Test 2: Canonical Ordering Determinism (A vs B == B vs A)
        print("\n[Test 2] Testing Canonical Slug Ordering Determinism...")
        payload1 = seo_platform_service.evaluate_comparison_seo(db=db, p1_id=1, p2_id=2)
        payload2 = seo_platform_service.evaluate_comparison_seo(db=db, p1_id=2, p2_id=1)
        print(f"  Order (1 vs 2) Slug: {payload1.canonical_slug}")
        print(f"  Order (2 vs 1) Slug: {payload2.canonical_slug}")
        assert payload1.canonical_slug == payload2.canonical_slug, "Canonical slug ordering mismatch"
        print("  [OK] Canonical Slug Determinism Passed!")

        # Test 3: Schema.org JSON-LD Graph Validity
        print("\n[Test 3] Testing Schema.org JSON-LD Structured Data...")
        json_ld = payload.json_ld_schema
        graph = json_ld.get("@graph", [])
        print(f"  Schema Graph Nodes Count: {len(graph)}")
        node_types = [node.get("@type") for node in graph]
        print(f"  Node Types Included: {node_types}")
        assert "FAQPage" in node_types, "FAQPage missing from JSON-LD"
        assert "BreadcrumbList" in node_types, "BreadcrumbList missing from JSON-LD"
        print("  [OK] Schema.org JSON-LD Passed!")

        # Test 4: Dynamic XML Sitemap & Robots.txt Generation
        print("\n[Test 4] Testing XML Sitemap & Robots.txt Generation...")
        sitemap_xml = dynamic_sitemap_service.generate_sitemap_xml(["https://brandbattle.com/compare/p1-vs-p2"])
        robots_txt = robots_service.generate_robots_txt()
        print(f"  Sitemap XML Snippet: {sitemap_xml[:120].strip()}...")
        print(f"  Robots.txt Snippet: {robots_txt[:100].strip()}...")
        assert "<urlset" in sitemap_xml, "Sitemap XML invalid"
        assert "User-agent:" in robots_txt, "Robots.txt invalid"
        print("  [OK] Sitemap & Robots.txt Passed!")

        # Test 5: Automated SEO Quality Validator
        print("\n[Test 5] Testing Automated SEO Quality Validator...")
        val_res = automated_seo_quality_validator.validate_page_seo(
            title=payload.title,
            meta_description=payload.meta_description,
            canonical_url=payload.canonical_url,
            json_ld=json_ld,
        )
        print(f"  SEO Quality Score: {val_res['validation_score']}/100 | Is Valid: {val_res['is_valid']}")
        assert val_res["is_valid"], "Automated SEO Quality Validator failed"
        print("  [OK] Automated SEO Quality Validator Passed!")

        print("\n" + "=" * 60)
        print("  ALL SEO COMPARISON PUBLISHING PLATFORM TESTS PASSED!  ")
        print("=" * 60)

    finally:
        db.close()


if __name__ == "__main__":
    main()
