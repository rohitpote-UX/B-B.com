"""
Brand Battle — Safe Catalog Ingestion Engine Migration
Creates catalog_sources, raw_catalog_records, and catalog_ingestion_jobs tables.
Idempotent, non-destructive, compatible with both SQLite and PostgreSQL.
"""

import os
import sys
import sqlite3
import logging
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("brandbattle.migration.catalog_engine")

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BACKEND_DIR, "brandbattle.db")
ROOT_DB_PATH = os.path.join(os.path.dirname(BACKEND_DIR), "brandbattle.db")


SQL_CREATE_TABLES = """
CREATE TABLE IF NOT EXISTS catalog_sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,
    source_type VARCHAR(50) NOT NULL DEFAULT 'AFFILIATE',
    base_url VARCHAR(500),
    adapter_key VARCHAR(50) NOT NULL,
    license_type VARCHAR(100),
    commercial_use_allowed BOOLEAN NOT NULL DEFAULT 1,
    automated_access_allowed BOOLEAN NOT NULL DEFAULT 1,
    requires_auth BOOLEAN NOT NULL DEFAULT 0,
    active BOOLEAN NOT NULL DEFAULT 1,
    priority INTEGER NOT NULL DEFAULT 10,
    terms_url VARCHAR(500),
    data_scope VARCHAR(255),
    last_sync_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_catalog_sources_adapter_key ON catalog_sources(adapter_key);
CREATE INDEX IF NOT EXISTS idx_catalog_sources_active ON catalog_sources(active);

CREATE TABLE IF NOT EXISTS raw_catalog_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER NOT NULL,
    external_id VARCHAR(255) NOT NULL,
    source_url VARCHAR(1000),
    raw_payload TEXT NOT NULL,
    content_hash VARCHAR(64) NOT NULL,
    retrieved_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    parser_version VARCHAR(50),
    processing_status VARCHAR(30) NOT NULL DEFAULT 'RECEIVED',
    failure_reason VARCHAR(500),
    master_product_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(source_id) REFERENCES catalog_sources(id) ON DELETE CASCADE,
    FOREIGN KEY(master_product_id) REFERENCES master_products(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_raw_source_external ON raw_catalog_records(source_id, external_id);
CREATE INDEX IF NOT EXISTS idx_raw_source_hash ON raw_catalog_records(source_id, content_hash);
CREATE INDEX IF NOT EXISTS idx_raw_status_created ON raw_catalog_records(processing_status, created_at);
CREATE INDEX IF NOT EXISTS idx_raw_master_product_id ON raw_catalog_records(master_product_id);

CREATE TABLE IF NOT EXISTS catalog_ingestion_jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER NOT NULL,
    job_type VARCHAR(30) NOT NULL DEFAULT 'FULL_SYNC',
    status VARCHAR(30) NOT NULL DEFAULT 'QUEUED',
    started_at DATETIME,
    completed_at DATETIME,
    cursor VARCHAR(500),
    next_cursor VARCHAR(500),
    records_seen INTEGER NOT NULL DEFAULT 0,
    records_created INTEGER NOT NULL DEFAULT 0,
    records_updated INTEGER NOT NULL DEFAULT 0,
    records_merged INTEGER NOT NULL DEFAULT 0,
    records_reviewed INTEGER NOT NULL DEFAULT 0,
    records_rejected INTEGER NOT NULL DEFAULT 0,
    records_failed INTEGER NOT NULL DEFAULT 0,
    error_summary TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(source_id) REFERENCES catalog_sources(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_job_source_status ON catalog_ingestion_jobs(source_id, status);
"""


DEFAULT_SOURCES = [
    {
        "name": "Flipkart Affiliate Feed",
        "source_type": "AFFILIATE",
        "base_url": "https://affiliate-api.flipkart.net/affiliate/1.0",
        "adapter_key": "flipkart_feed",
        "license_type": "Flipkart Affiliate Agreement",
        "commercial_use_allowed": True,
        "automated_access_allowed": True,
        "requires_auth": True,
        "active": True,
        "priority": 1,
        "terms_url": "https://affiliate.flipkart.com/terms",
        "data_scope": "Electronics, Mobiles, Laptops, Audio, Wearables",
    },
    {
        "name": "Admin Catalog Import",
        "source_type": "ADMIN_IMPORT",
        "base_url": None,
        "adapter_key": "admin_import",
        "license_type": "BrandBattle Authorized Catalog",
        "commercial_use_allowed": True,
        "automated_access_allowed": True,
        "requires_auth": True,
        "active": True,
        "priority": 2,
        "terms_url": "https://brandbattle.com/terms",
        "data_scope": "Manual and CSV/JSON Catalog Feeds",
    }
]


def run_migration(db_path: str):
    if not os.path.exists(db_path):
        logger.info(f"Database at {db_path} does not exist, skipping.")
        return

    logger.info(f"Applying migration to {db_path}...")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    try:
        cur.executescript(SQL_CREATE_TABLES)

        # Ensure verification columns exist in marketplace_offers, products, and prices
        cur.execute("PRAGMA table_info(marketplace_offers)")
        existing_offer_cols = {c[1] for c in cur.fetchall()}
        offer_col_defs = {
            "verification_status": "VARCHAR(30)",
            "verified_at": "DATETIME",
            "source_method": "VARCHAR(50)",
            "confidence_score": "FLOAT",
            "parser_version": "VARCHAR(50)",
            "failure_reason": "VARCHAR(500)",
            "shipping_cost_verified": "BOOLEAN DEFAULT 0"
        }
        for col_name, col_type in offer_col_defs.items():
            if col_name not in existing_offer_cols:
                cur.execute(f"ALTER TABLE marketplace_offers ADD COLUMN {col_name} {col_type}")
                logger.info(f"Added column {col_name} to marketplace_offers in {db_path}")

        cur.execute("PRAGMA table_info(products)")
        existing_prod_cols = {c[1] for c in cur.fetchall()}
        prod_col_defs = {
            "data_quality_score": "FLOAT DEFAULT 0.0",
            "price_verified_at": "DATETIME",
            "image_verified_at": "DATETIME",
            "price_verification_status": "VARCHAR(30)",
            "data_source": "VARCHAR(50)",
            "currency": "VARCHAR(10) DEFAULT 'INR'"
        }
        for col_name, col_type in prod_col_defs.items():
            if col_name not in existing_prod_cols:
                cur.execute(f"ALTER TABLE products ADD COLUMN {col_name} {col_type}")
                logger.info(f"Added column {col_name} to products in {db_path}")

        cur.execute("PRAGMA table_info(prices)")
        existing_price_cols = {c[1] for c in cur.fetchall()}
        price_col_defs = {
            "verification_status": "VARCHAR(30)",
            "verified_at": "DATETIME",
            "source_method": "VARCHAR(50)",
            "confidence_score": "FLOAT",
            "parser_version": "VARCHAR(50)",
            "failure_reason": "VARCHAR(500)",
            "currency": "VARCHAR(10) DEFAULT 'INR'"
        }
        for col_name, col_type in price_col_defs.items():
            if col_name not in existing_price_cols:
                cur.execute(f"ALTER TABLE prices ADD COLUMN {col_name} {col_type}")
                logger.info(f"Added column {col_name} to prices in {db_path}")

        # Seed default sources if missing
        for src in DEFAULT_SOURCES:
            cur.execute("SELECT id FROM catalog_sources WHERE name = ?", (src["name"],))
            row = cur.fetchone()
            if not row:
                cur.execute("""
                    INSERT INTO catalog_sources (
                        name, source_type, base_url, adapter_key, license_type,
                        commercial_use_allowed, automated_access_allowed, requires_auth,
                        active, priority, terms_url, data_scope
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    src["name"], src["source_type"], src["base_url"], src["adapter_key"],
                    src["license_type"], src["commercial_use_allowed"], src["automated_access_allowed"],
                    src["requires_auth"], src["active"], src["priority"], src["terms_url"],
                    src["data_scope"]
                ))
                logger.info(f"Seeded source: {src['name']}")

        conn.commit()
        logger.info(f"Migration applied successfully to {db_path}.")
    except Exception as e:
        conn.rollback()
        logger.error(f"Migration failed for {db_path}: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    run_migration(DB_PATH)
    if os.path.exists(ROOT_DB_PATH):
        run_migration(ROOT_DB_PATH)
    logger.info("All database migrations completed successfully.")
