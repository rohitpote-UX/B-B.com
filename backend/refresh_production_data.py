"""
Brand Battle — Production Data Refresh CLI Runner
Executes Two-Stage Production Data Refresh and outputs the comprehensive production report.

Usage:
    python refresh_production_data.py --stage1-only
    python refresh_production_data.py --dry-run
    python refresh_production_data.py --full-refresh
"""

import sys
import os
import argparse
import json
import logging
from datetime import datetime, timezone

# Ensure backend root is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from database import SessionLocal
import models
from pipeline.production_refresh import production_refresh_engine, Stage1Report, Stage2Report

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("brandbattle.refresh_runner")


def print_stage1_report(report: Stage1Report):
    print("\n" + "=" * 70)
    print("           STAGE 1: DISCOVERY & COLLECTION REPORT            ")
    print("=" * 70)
    print(f"Total Marketplace Records Discovered : {report.total_discovered}")
    print(f"Successfully Parsed & Staged         : {report.successfully_parsed}")
    print(f"Failed Parsing                       : {report.failed_parsing}")
    print(f"Duplicate Records Skipped            : {report.duplicate_records}")
    print(f"Suspicious Records Quarantined       : {report.suspicious_records}")
    print(f"Missing Images Detected              : {report.missing_images}")
    print(f"Official API Successes               : {report.api_successes}")
    print(f"Official API Failures (Fell to Feed) : {report.api_failures}")
    print(f"Scraper Unhandled Failures           : {report.scraper_failures}")
    print("\n--- Discovery Breakdown by Marketplace ---")
    for mp, stats in report.by_marketplace.items():
        print(f"  [{mp.upper():16s}] Discovered: {stats['discovered']:4d} | Parsed: {stats['parsed']:4d} | Suspicious: {stats['suspicious']:2d} | Failed: {stats['failed']:2d}")
    print("=" * 70)


def print_stage2_report(report: Stage2Report, db):
    print("\n" + "=" * 70)
    print("     STAGE 2: VALIDATION, VERIFICATION & PROMOTION REPORT    ")
    print("=" * 70)
    print(f"Pre-Promotion Backup Snapshot        : {report.backup_file or 'N/A'}")
    print(f"Total Offers Promoted/Updated        : {report.total_promoted}")
    print(f"Price Verified Offers                : {report.price_verified}")
    print(f"Price Unverified Offers              : {report.price_unverified}")
    print(f"Price Anomalies Quarantined          : {report.price_anomalies_quarantined}")
    print(f"Image Verified                       : {report.image_verified}")
    print(f"Image Verification Failed            : {report.image_failed}")
    print(f"Borderline Matches Enqueued          : {report.borderline_matches_reviewed}")
    print(f"Price Drop Alerts Triggered          : {report.alerts_triggered}")
    print(f"Targeted Cache Keys Purged           : {report.cache_keys_invalidated}")
    print(f"Orphan Products in Catalog           : {report.orphan_products_count}")
    print("\n--- Marketplace Promotion Statistics ---")
    for mp, stats in report.by_marketplace.items():
        print(f"  [{mp.upper():16s}] Checked: {stats['checked']:4d} | Updated: {stats['updated']:4d} | Verified: {stats['verified']:4d} | Quarantined: {stats['quarantined']:2d}")

    print("\n" + "-" * 70)
    print(f"  DATA TRUST SCORE: {report.data_trust_score} / 100")
    print("-" * 70)
    for dim, val in report.trust_score_breakdown.items():
        print(f"    - {dim.replace('_', ' ').title():28s}: {val:5.1f} pts")

    print("\n" + "-" * 70)
    print(f"  HARD RELEASE GATES: {'PASSED [DEPLOYMENT AUTHORIZED]' if report.hard_release_gates_passed else 'FAILED [DEPLOYMENT BLOCKED]'}")
    print("-" * 70)
    for gate, passed in report.gate_details.items():
        status_icon = "PASS" if passed else "FAIL"
        print(f"    [{status_icon}] {gate.replace('_', ' ').title()}")
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(description="Brand Battle Production Data Refresh CLI")
    parser.add_argument("--stage1-only", action="store_true", help="Run Stage 1 Discovery without promoting")
    parser.add_argument("--dry-run", action="store_true", help="Execute Stage 1 and Stage 2 without committing DB changes")
    parser.add_argument("--full-refresh", action="store_true", help="Execute complete Stage 1 & Stage 2 production refresh")
    parser.add_argument("--limit", type=int, default=None, help="Limit observations per marketplace (for testing)")

    args = parser.parse_args()

    # Default to full-refresh if no flag passed
    if not args.stage1_only and not args.dry_run and not args.full_refresh:
        args.full_refresh = True

    print("=" * 70)
    print("  BRAND BATTLE — FINAL PRODUCTION DATA REFRESH & VERIFICATION  ")
    print("=" * 70)
    print(f"Timestamp : {datetime.now(timezone.utc).isoformat()}")
    print(f"Mode      : {'STAGE 1 ONLY' if args.stage1_only else ('DRY RUN' if args.dry_run else 'FULL PRODUCTION REFRESH')}")
    print("=" * 70)

    # 1. Run Stage 1 Discovery
    staged_items, stage1_report = production_refresh_engine.run_stage1_discovery(
        limit_per_marketplace=args.limit
    )
    print_stage1_report(stage1_report)

    if args.stage1_only:
        print("\n✅ Stage 1 complete. Promotion skipped as requested.")
        return

    # 2. Run Stage 2 Promotion
    db = SessionLocal()
    try:
        stage2_report = production_refresh_engine.run_stage2_promotion(
            staged_items=staged_items,
            db=db,
            dry_run=args.dry_run
        )
        print_stage2_report(stage2_report, db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
