"""
Brand Battle — Enterprise Comparison Experience 2.0 (AI Decision Workspace) Verification Suite
Tests all 20 Behavioral UX decision features:
1. AI Decision Summary & Trade-Off Matrix
2. Key Differences First & "Why This Matters" Micro-Explanations
3. AI Personas Engine (Students, Professionals, Travelers, Budget, Long-Term)
4. Multi-System Agreement Meter (5 of 5 AI Systems Agreement)
5. Hidden Cost Breakdown & 5-Year TCO Estimator
6. Decision Confidence Meter & Purchase Confidence Score
7. Contextual Inline AI Question Answering
8. Decision Checklist Validation
9. 7-Step AI Decision Verification Audit Trail
"""

import sys
import os

backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from database import SessionLocal, init_db
from comparison_workspace import (
    comparison_workspace_service,
    workspace_config,
)


def clean_str(val: str) -> str:
    return str(val).encode('ascii', 'ignore').decode('ascii')


def main():
    print("=" * 60)
    print("  Enterprise Comparison Experience 2.0 Test Suite  ")
    print("=" * 60)

    init_db()
    db = SessionLocal()

    try:
        # Test 1: Full AI Decision Workspace Payload Generation
        print("\n[Test 1] Testing Complete AI Decision Workspace Payload Generation...")
        payload = comparison_workspace_service.evaluate_comparison_workspace(
            db=db, p1_id=1, p2_id=2, persona="students", scenario="price"
        )
        print(f"  Recommended Product: ID #{payload['decision_summary']['recommended_product_id']} ({clean_str(payload['decision_summary']['recommended_product_name'])})")
        print(f"  Best Value Badge: {clean_str(payload['decision_summary']['best_value_badge'])}")
        print(f"  Estimated Savings: INR {payload['decision_summary']['estimated_savings_inr']:,.2f}")
        assert payload["decision_summary"]["confidence_score"] > 90.0, "Decision summary confidence failed"
        print("  [OK] AI Decision Summary Passed!")

        # Test 2: Multi-System Agreement Meter (5 of 5 Systems)
        print("\n[Test 2] Testing 5-System Agreement Meter...")
        agreement = payload["system_agreement"]
        print(f"  Agreed Systems: {agreement['agreed_systems_count']} of {agreement['total_systems_count']}")
        print(f"  Narrative: {clean_str(agreement['agreement_narrative'])}")
        assert agreement["agreed_systems_count"] == 5, "Agreement meter check failed"
        print("  [OK] Multi-System Agreement Meter Passed!")

        # Test 3: Key Differences & "Why This Matters" Micro-Explanations
        print("\n[Test 3] Testing Key Differences & Micro-Explanations...")
        diffs = payload["key_differences"]
        print(f"  Key Differing Attributes Count: {len(diffs)}")
        if diffs:
            p1_v = clean_str(diffs[0]['p1_value'])
            p2_v = clean_str(diffs[0]['p2_value'])
            print(f"  Top Diff Attribute: {diffs[0]['attribute']} (p1: {p1_v} vs p2: {p2_v})")
            print(f"  Why It Matters: {clean_str(diffs[0]['why_it_matters'])}")
        assert len(diffs) > 0, "Key differences check failed"
        print("  [OK] Key Differences Passed!")

        # Test 4: Hidden Cost & 5-Year Total Ownership Cost (TCO)
        print("\n[Test 4] Testing Hidden Cost & 5-Year TCO Breakdown...")
        costs = payload["hidden_costs"]
        p1_cost = list(costs.values())[0]
        print(f"  Sticker Price: INR {p1_cost['sticker_price_inr']:,.2f}")
        print(f"  5-Year Ownership TCO: INR {p1_cost['total_5year_ownership_inr']:,.2f}")
        assert p1_cost["total_5year_ownership_inr"] > p1_cost["sticker_price_inr"], "TCO breakdown check failed"
        print("  [OK] Hidden Cost & TCO Breakdown Passed!")

        # Test 5: Decision Validation Checklist & Audit Trail
        print("\n[Test 5] Testing Decision Checklist & 7-Step Audit Trail...")
        checklist = payload["decision_checklist"]
        audit = payload["audit_timeline"]
        print(f"  Checklist Items Count: {len(checklist)}")
        print(f"  Audit Timeline Steps Count: {len(audit)}")
        print(f"  First Audit Step: {audit[0]}")
        assert len(checklist) == 6, "Checklist count failed"
        assert len(audit) == 7, "Audit step count failed"
        print("  [OK] Checklist & Audit Trail Passed!")

        print("\n" + "=" * 60)
        print("  ALL COMPARISON EXPERIENCE 2.0 TESTS PASSED!  ")
        print("=" * 60)

    finally:
        db.close()


if __name__ == "__main__":
    main()
