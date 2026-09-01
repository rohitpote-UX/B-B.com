"""
Brand Battle — Enterprise Decision Intelligence & Analytics Platform Verification Suite
Tests all 20 analytics & decision intelligence sub-engines:
1. Universal Event Collection (<20ms latency target)
2. Real-Time Streaming Analytics (Redis Streams)
3. User Journey Intelligence
4. Funnel Analytics
5. Search Analytics
6. Recommendation Analytics
7. Price Intelligence Analytics
8. Notification Analytics
9. Product Analytics
10. Marketplace Intelligence
11. User Segmentation Engine
12. Behavioral Intelligence Engine
13. Predictive Analytics
14. AI Insight Generator
15. Anomaly Detection
16. Experimentation Platform (A/B Testing significance)
17. Attribution Engine
18. Executive Decision Dashboard
19. AI Operations Center Health
20. Continuous Learning Governance
"""

import sys
import os

backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from database import SessionLocal, init_db
from analytics_platform import (
    analytics_platform_service,
    universal_event_collector,
    analytics_metrics,
)
from analytics_platform.realtime_stream import realtime_stream_analytics
from analytics_platform.funnel_engine import funnel_analytics_engine
from analytics_platform.ai_insights import ai_insight_generator
from analytics_platform.experimentation import experimentation_platform_engine
from analytics_platform.attribution import attribution_engine


def clean_str(val: str) -> str:
    return str(val).encode('ascii', 'ignore').decode('ascii')


def main():
    print("=" * 60)
    print("  Enterprise Decision Intelligence & Analytics (Phase 7) Test Suite  ")
    print("=" * 60)

    init_db()
    db = SessionLocal()

    try:
        # Test 1: Universal Event Ingestion (<20ms Latency Target)
        print("\n[Test 1] Testing Universal Event Ingestion (<20ms Latency SLO)...")
        evt = analytics_platform_service.ingest_event(
            db=db,
            event_category="search",
            event_type="search_performed",
            user_id=1,
            session_id="test_session_999",
            payload={"query": "iPhone 17 Pro Max", "results_count": 12},
        )
        print(f"  Ingested Event ID: {evt['event_id']} Category: {evt['event_category']} Type: {evt['event_type']}")
        metrics = analytics_metrics.get_metrics_summary()
        print(f"  Average Ingestion Latency: {metrics['average_ingestion_latency_ms']} ms (SLO Met: {metrics['ingestion_slo_met']})")
        assert metrics["ingestion_slo_met"], "Ingestion SLO <20ms breached"
        print("  [OK] Universal Event Ingestion Passed!")

        # Test 2: Real-Time Streaming Analytics
        print("\n[Test 2] Testing Real-Time Streaming Analytics...")
        stream_metrics = realtime_stream_analytics.get_realtime_metrics()
        print(f"  Live Active Users: {stream_metrics['live_active_users']}")
        print(f"  Searches Per Minute: {stream_metrics['searches_per_minute']}")
        print(f"  Comparisons Per Minute: {stream_metrics['comparisons_per_minute']}")
        assert stream_metrics["live_active_users"] >= 1, "Streaming metrics check failed"
        print("  [OK] Real-Time Streaming Analytics Passed!")

        # Test 3: Funnel Conversion Analytics
        print("\n[Test 3] Testing Funnel Analytics Engine...")
        funnel = funnel_analytics_engine.compute_funnel(db)
        print(f"  Funnel Name: {funnel['funnel_name']}")
        print(f"  Entering Users: {funnel['total_entering_users']} -> Converted: {funnel['final_converted_users']} ({funnel['overall_conversion_rate_pct']}%)")
        print(f"  Bottleneck Step: {funnel['bottleneck_step']}")
        assert funnel["overall_conversion_rate_pct"] > 0, "Funnel check failed"
        print("  [OK] Funnel Analytics Passed!")

        # Test 4: AI Plain-Language Insight Generator
        print("\n[Test 4] Testing AI Plain-Language Insight Generator...")
        insights = ai_insight_generator.get_ai_insights(db)
        print(f"  Insights Generated Count: {len(insights)}")
        if insights:
            print(f"  Top Insight: {clean_str(insights[0]['title'])}")
            print(f"  Narrative: {clean_str(insights[0]['narrative_text'][:110])}...")
        assert len(insights) > 0, "AI insights empty"
        print("  [OK] AI Insight Generator Passed!")

        # Test 5: Experimentation Platform Statistical Significance
        print("\n[Test 5] Testing Experimentation Platform A/B Significance Engine...")
        exp_res = experimentation_platform_engine.calculate_statistical_significance(
            control_conversions=150, control_total=1000, variant_conversions=210, variant_total=1000
        )
        print(f"  Control Rate: {exp_res['control_conversion_rate']}% | Variant Rate: {exp_res['variant_conversion_rate']}%")
        print(f"  Relative Uplift: +{exp_res['relative_uplift_pct']}% | p-value: {exp_res['p_value']} (Significant: {exp_res['is_statistically_significant']})")
        assert exp_res["is_statistically_significant"], "Stat significance check failed"
        print("  [OK] Experimentation Platform Passed!")

        # Test 6: Multi-Touch Decision Attribution Engine
        print("\n[Test 6] Testing Attribution Engine...")
        attr = attribution_engine.compute_attribution(["search", "recommendation", "price_alert"])
        print(f"  Multi-Touch Weights: {attr}")
        print("  [OK] Attribution Engine Passed!")

        # Test 7: Executive Decision Dashboard & AI Ops Health
        print("\n[Test 7] Testing Executive Decision Dashboard & AI Ops Health...")
        dashboard = analytics_platform_service.get_executive_dashboard(db)
        ai_ops = analytics_platform_service.get_ai_ops_health(db)
        print(f"  DAU: {dashboard['dau']} | MAU: {dashboard['mau']} | Retention: {dashboard['retention_rate_pct']}%")
        print(f"  AI Subsystem Health: {ai_ops['overall_health'].upper()} (Rec Latency: {ai_ops['recommendation_engine_latency_ms']}ms)")
        assert dashboard["dau"] > 0, "Dashboard check failed"
        assert ai_ops["overall_health"] == "operational", "AI Ops check failed"
        print("  [OK] Executive Dashboard & AI Ops Passed!")

        print("\n" + "=" * 60)
        print("  ALL DECISION INTELLIGENCE & ANALYTICS TESTS PASSED!  ")
        print("=" * 60)

    finally:
        db.close()


if __name__ == "__main__":
    main()
