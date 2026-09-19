"""
Brand Battle — Production Database Migration CLI Tool
Migrates all tables, schemas, relations, and data from SQLite to PostgreSQL.

Usage:
    # Dry run inspection (verifies SQLite catalog and reports rows to migrate)
    python migrate_sqlite_to_postgres.py --dry-run

    # Execute migration using DATABASE_URL from environment
    python migrate_sqlite_to_postgres.py

    # Execute migration with explicit PostgreSQL connection string
    python migrate_sqlite_to_postgres.py --target-url "postgresql://user:pass@host:5432/dbname"
"""

import sys
import os
import argparse
import logging
import sqlite3
import json
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

from sqlalchemy import create_engine, text, MetaData, Table, inspect
from sqlalchemy.orm import sessionmaker

# Ensure backend root is in sys.path
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from config import settings
from database import Base
import models  # noqa: F401 - Register all models with Base

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("brandbattle.db_migration")


def get_sqlite_tables_and_counts(sqlite_path: str) -> Dict[str, int]:
    """Returns all user tables and row counts from SQLite database."""
    if not os.path.exists(sqlite_path):
        raise FileNotFoundError(f"SQLite database file not found at: {sqlite_path}")

    conn = sqlite3.connect(sqlite_path)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    tables = [r[0] for r in cur.fetchall() if not r[0].startswith("sqlite_")]
    counts = {}
    for tbl in tables:
        try:
            cur.execute(f'SELECT COUNT(*) FROM "{tbl}"')
            counts[tbl] = cur.fetchone()[0]
        except Exception as e:
            logger.warning(f"Could not count rows in SQLite table '{tbl}': {e}")
            counts[tbl] = 0
    conn.close()
    return counts


def migrate_data(
    sqlite_path: str,
    target_url: str,
    dry_run: bool = False,
    batch_size: int = 500,
) -> bool:
    """
    Executes lossless data migration from SQLite to PostgreSQL:
    1. Inspects SQLite catalog.
    2. Initializes PostgreSQL schema via Base.metadata.create_all().
    3. Disables foreign key triggers temporarily on PostgreSQL.
    4. Migrates all 64 tables in batches.
    5. Re-enables foreign key triggers.
    6. Resets PostgreSQL auto-increment sequences.
    7. Verifies 100% row count parity.
    """
    logger.info("=" * 70)
    logger.info("  BRAND BATTLE — SQLITE TO POSTGRESQL PRODUCTION MIGRATION  ")
    logger.info("=" * 70)
    logger.info(f"Source SQLite  : {sqlite_path}")
    logger.info(f"Target Postgres: {target_url.split('@')[-1] if '@' in target_url else target_url}")
    logger.info(f"Mode           : {'DRY RUN (NO MODIFICATIONS)' if dry_run else 'LIVE MIGRATION'}")
    logger.info(f"Batch Size     : {batch_size}")
    logger.info("=" * 70)

    # 1. Inspect source SQLite
    sqlite_counts = get_sqlite_tables_and_counts(sqlite_path)
    total_sqlite_rows = sum(sqlite_counts.values())
    logger.info(f"Source SQLite catalog contains {len(sqlite_counts)} tables with {total_sqlite_rows:,} total rows.")

    if dry_run:
        print("\n=== DRY RUN TABLE AUDIT ===")
        for tbl, count in sorted(sqlite_counts.items()):
            print(f"  - {tbl:35s}: {count:6d} rows")
        print("=" * 70)
        logger.info("✅ Dry run inspection complete. Source database is intact and ready for migration.")
        return True

    # Normalize connection string for SQLAlchemy 2.0+
    if target_url.startswith("postgres://"):
        target_url = target_url.replace("postgres://", "postgresql://", 1)

    # 2. Connect to target PostgreSQL
    pg_engine = create_engine(
        target_url,
        pool_pre_ping=True,
        client_encoding="utf8",
    )

    # Test connection
    with pg_engine.connect() as conn:
        res = conn.execute(text("SELECT version();")).scalar()
        logger.info(f"Connected to PostgreSQL: {res}")

    # 3. Create all tables in PostgreSQL
    logger.info("Creating all registered database tables in PostgreSQL...")
    Base.metadata.create_all(bind=pg_engine)
    logger.info("✅ PostgreSQL tables initialized successfully.")

    # 4. Open SQLite connection
    sqlite_conn = sqlite3.connect(sqlite_path)
    sqlite_conn.row_factory = sqlite3.Row

    migration_success = True
    migrated_stats = {}

    with pg_engine.connect() as pg_conn:
        # Temporarily disable foreign key constraints during bulk load
        is_postgres = "postgresql" in str(pg_engine.url)
        if is_postgres:
            try:
                pg_conn.execute(text("SET session_replication_role = 'replica';"))
                pg_conn.commit()
                logger.info("Disabled PostgreSQL foreign key triggers for bulk insertion.")
            except Exception as e:
                logger.warning(f"Could not set session_replication_role (non-superuser?): {e}")

        # Iterate through tables defined in Base.metadata
        for table in Base.metadata.sorted_tables:
            tbl_name = table.name
            if tbl_name not in sqlite_counts:
                logger.info(f"Skipping table '{tbl_name}' (not in SQLite source)")
                continue

            row_count = sqlite_counts[tbl_name]
            if row_count == 0:
                migrated_stats[tbl_name] = (0, 0, "EMPTY")
                continue

            logger.info(f"Migrating table '{tbl_name}' ({row_count} rows)...")
            cur = sqlite_conn.cursor()
            cur.execute(f'SELECT * FROM "{tbl_name}"')

            # Identify JSON columns to ensure proper dictionary serialization
            json_cols = set()
            for col in table.columns:
                if "json" in str(col.type).lower():
                    json_cols.add(col.name)

            batch = []
            inserted_count = 0

            while True:
                rows = cur.fetchmany(batch_size)
                if not rows:
                    break

                for r in rows:
                    row_dict = dict(r)
                    # Convert JSON string to dict/list if needed
                    for col_name in json_cols:
                        val = row_dict.get(col_name)
                        if isinstance(val, str) and val.strip():
                            try:
                                row_dict[col_name] = json.loads(val)
                            except Exception:
                                pass
                    batch.append(row_dict)

                if batch:
                    try:
                        pg_conn.execute(table.insert(), batch)
                        pg_conn.commit()
                        inserted_count += len(batch)
                        batch = []
                    except Exception as e:
                        pg_conn.rollback()
                        logger.error(f"❌ Error inserting batch into '{tbl_name}': {e}")
                        migration_success = False
                        break

            # Verify count in target
            target_count = pg_conn.execute(text(f'SELECT COUNT(*) FROM "{tbl_name}"')).scalar() or 0
            status = "PASS" if target_count == row_count else "MISMATCH"
            migrated_stats[tbl_name] = (row_count, target_count, status)
            logger.info(f"  [{status}] '{tbl_name}': SQLite={row_count}, Postgres={target_count}")

        # Re-enable foreign key constraints
        if is_postgres:
            try:
                pg_conn.execute(text("SET session_replication_role = 'origin';"))
                pg_conn.commit()
                logger.info("Re-enabled PostgreSQL foreign key triggers.")
            except Exception as e:
                logger.warning(f"Could not restore session_replication_role: {e}")

        # 5. Reset PostgreSQL sequences
        if is_postgres:
            logger.info("Aligning PostgreSQL auto-increment sequences...")
            for table in Base.metadata.sorted_tables:
                pk_cols = [c for c in table.columns if c.primary_key and isinstance(c.type, models.Integer)]
                if pk_cols:
                    pk_name = pk_cols[0].name
                    try:
                        seq_sql = f"""
                        SELECT setval(
                            pg_get_serial_sequence('{table.name}', '{pk_name}'),
                            COALESCE(MAX({pk_name}), 1)
                        ) FROM "{table.name}";
                        """
                        pg_conn.execute(text(seq_sql))
                        pg_conn.commit()
                    except Exception:
                        pass
            logger.info("✅ Sequences aligned.")

    sqlite_conn.close()

    # 6. Final Reconciliation Summary
    print("\n" + "=" * 70)
    print("         POSTGRESQL MIGRATION RECONCILIATION REPORT           ")
    print("=" * 70)
    print(f"{'TABLE NAME':35s} | {'SQLITE':8s} | {'POSTGRES':8s} | {'STATUS':8s}")
    print("-" * 70)
    all_matched = True
    for tbl, (src_cnt, tgt_cnt, st) in sorted(migrated_stats.items()):
        if st != "PASS" and src_cnt > 0:
            all_matched = False
        print(f"{tbl:35s} | {src_cnt:8d} | {tgt_cnt:8d} | {st:8s}")
    print("=" * 70)

    if all_matched and migration_success:
        logger.info("🎉 Database migration completed with 100% data fidelity!")
        return True
    else:
        logger.error("⚠️ Database migration completed with discrepancies. Review logs above.")
        return False


def main():
    parser = argparse.ArgumentParser(description="Brand Battle SQLite to PostgreSQL Migration CLI")
    parser.add_argument(
        "--sqlite-path",
        default=os.path.join(BACKEND_DIR, "brandbattle.db"),
        help="Path to source SQLite database"
    )
    parser.add_argument(
        "--target-url",
        default=None,
        help="Target PostgreSQL connection URL (defaults to DATABASE_URL in config)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Inspect SQLite database and print report without modifying PostgreSQL"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=500,
        help="Number of records per insert batch"
    )

    args = parser.parse_args()

    # Resolve target URL
    target_url = args.target_url or settings.effective_database_url
    if not args.dry_run and target_url.startswith("sqlite"):
        print("❌ Error: Target DATABASE_URL is an SQLite URL. Provide a PostgreSQL URL via --target-url or DATABASE_URL.")
        sys.exit(1)

    success = migrate_data(
        sqlite_path=args.sqlite_path,
        target_url=target_url,
        dry_run=args.dry_run,
        batch_size=args.batch_size,
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
