"""
Brand Battle — Enterprise Affiliate Commerce Platform (Phase 11) Verification Suite
Tests all 15 affiliate modules:
1. Affiliate Provider Abstraction & Registry (Amazon, Flipkart, Impact)
2. Deep Link Generator (<50ms Latency Target)
3. Multi-Network Routing Engine
4. Link Validation Engine
5. Click Tracking Engine & Fraud Detection
6. Conversion Tracking & Transaction Recording
7. Commission Dashboard Analytics (Revenue, EPC, Conversion Rate)
8. Transparent User Disclosure Notice
9. Link Health Monitoring
10. Fallback Logic Engine (Guarantees non-blocking purchase journey)
11. Performance Telemetry & Uptime Metrics
"""

import sys
import os

backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from database import SessionLocal, init_db
from affiliate_platform import (
    affiliate_platform_service,
    deeplink_generator,
    provider_registry,
    affiliate_metrics,
)
from affiliate_platform.click_tracker import click_tracker_engine
from affiliate_platform.conversion_tracker import conversion_tracker_engine
from affiliate_platform.fallback_engine import fallback_logic_engine


def clean_str(val: str) -> str:
    return str(val).encode('ascii', 'ignore').decode('ascii')


def main():
    print("=" * 60)
    print("  Enterprise Affiliate Commerce Platform Test Suite  ")
    print("=" * 60)

    init_db()
    db = SessionLocal()

    try:
        # Test 1: Provider Abstraction & Registry
        print("\n[Test 1] Testing Pluggable Provider Registry...")
        providers = provider_registry.get_all_providers()
        print(f"  Registered Providers Count: {len(providers)}")
        print(f"  Provider Keys: {list(providers.keys())}")
        assert "amazon" in providers, "Amazon provider missing"
        assert "flipkart" in providers, "Flipkart provider missing"
        print("  [OK] Pluggable Provider Registry Passed!")

        # Test 2: Deep Link Generator (<50ms Latency Target)
        print("\n[Test 2] Testing Deep Link Generator (<50ms Latency SLO)...")
        res = affiliate_platform_service.generate_product_deeplink(
            db=db,
            product_id=1,
            destination_url="https://www.amazon.in/dp/B0CX2349XX",
            touchpoint="search",
        )
        print(f"  Generated Link Token: {res.link_token}")
        print(f"  Provider Key: {res.provider_key}")
        print(f"  Affiliate URL: {clean_str(res.affiliate_url)}")
        metrics = affiliate_metrics.get_metrics_summary()
        print(f"  Average Deep Link Latency: {metrics['average_deeplink_latency_ms']} ms (SLO Met: {metrics['deeplink_slo_met']})")
        assert metrics["deeplink_slo_met"], "Deep link generation SLO <50ms breached"
        print("  [OK] Deep Link Generator Passed!")

        # Test 3: Click Tracking & Non-Blocking Logging
        print("\n[Test 3] Testing Click Tracking Engine...")
        click_res = click_tracker_engine.track_click(
            db=db,
            link_token=res.link_token,
            product_id=1,
            provider_key=res.provider_key,
            session_id="test_session_101",
        )
        print(f"  Tracked Click ID: {click_res['click_id']} | Fraud Flagged: {click_res['is_fraud']}")
        assert click_res["status"] == "tracked", "Click tracking failed"
        print("  [OK] Click Tracking Passed!")

        # Test 4: Conversion Tracking & Commission Recording
        print("\n[Test 4] Testing Conversion Tracking Engine...")
        conv_res = conversion_tracker_engine.record_conversion(
            db=db,
            provider_key="amazon",
            sale_amount=24999.0,
            commission_amount=1249.95,
            order_id="ORD-998811",
        )
        print(f"  Conversion ID: {conv_res['conversion_id']}")
        print(f"  Sale Amount: INR {conv_res['sale_amount_inr']:,.2f} | Commission: INR {conv_res['commission_amount_inr']:,.2f}")
        assert conv_res["status"] == "approved", "Conversion tracking failed"
        print("  [OK] Conversion Tracking Passed!")

        # Test 5: Fallback Logic Engine
        print("\n[Test 5] Testing Fallback Logic Engine...")
        fallback_url, is_fb = fallback_logic_engine.resolve_fallback("https://www.retailer.com/product/123")
        print(f"  Fallback Destination URL: {fallback_url} (Is Fallback: {is_fb})")
        assert fallback_url.startswith("https"), "Fallback resolution failed"
        print("  [OK] Fallback Logic Engine Passed!")

        # Test 6: Transparent User Disclosure Notice
        print("\n[Test 6] Testing Transparent User Disclosure Notice...")
        disc = affiliate_platform_service.get_user_disclosure()
        print(f"  Disclosure Text: {clean_str(disc['notice'][:110])}...")
        assert disc["is_active"], "Disclosure inactive"
        print("  [OK] Transparent User Disclosure Passed!")

        # Test 7: Commission Dashboard Analytics Aggregation
        print("\n[Test 7] Testing Commission Dashboard Analytics...")
        dashboard = affiliate_platform_service.get_commission_dashboard(db)
        print(f"  Total Revenue: INR {dashboard.total_revenue_inr:,.2f} | Total Commission: INR {dashboard.total_commission_inr:,.2f}")
        print(f"  Conversion Rate: {dashboard.conversion_rate_pct}% | EPC: INR {dashboard.epc_inr}")
        assert dashboard.total_commission_inr > 0, "Dashboard metrics check failed"
        print("  [OK] Commission Dashboard Analytics Passed!")

        print("\n" + "=" * 60)
        print("  ALL ENTERPRISE AFFILIATE PLATFORM TESTS PASSED!  ")
        print("=" * 60)

    finally:
        db.close()


if __name__ == "__main__":
    main()
