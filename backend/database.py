"""
Brand Battle - Database Configuration
SQLAlchemy engine, session management, and base model class.
Supports PostgreSQL (production) with connection pooling and SQLite (development).
"""

from sqlalchemy import create_engine, event, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings

db_url = settings.effective_database_url
is_sqlite = db_url.startswith("sqlite")

# Engine configuration
engine_kwargs = {}
if is_sqlite:
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    # Production-ready PostgreSQL connection pooling
    engine_kwargs["pool_size"] = 20
    engine_kwargs["max_overflow"] = 30
    engine_kwargs["pool_pre_ping"] = True
    engine_kwargs["pool_recycle"] = 1800
    engine_kwargs["client_encoding"] = "utf8"

engine = create_engine(db_url, **engine_kwargs)

# Enable WAL mode for SQLite (better concurrent read performance in dev)
if is_sqlite:
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency for FastAPI endpoints to get a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db_health() -> bool:
    """Returns True if database connection is alive and responding."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"⚠️ Database health check failed: {e}")
        return False


def init_db():
    """Create all tables and perform safe migrations / seeding if needed."""
    import models  # noqa: F401 - Import to register models with Base
    Base.metadata.create_all(bind=engine)

    # Safe column migrations for SQLite development DB
    if is_sqlite:
        try:
            with engine.connect() as conn:
                # Helper for safe column addition
                def add_col_if_missing(table_name, col_name, col_type):
                    res = conn.execute(text(f"PRAGMA table_info({table_name})")).fetchall()
                    cols = [row[1] for row in res]
                    if cols and col_name not in cols:
                        conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type}"))
                        conn.commit()
                        print(f"[OK] Added {col_name} column to {table_name} table")

                # products table additions
                add_col_if_missing("products", "master_product_id", "INTEGER REFERENCES master_products(id)")
                add_col_if_missing("products", "data_quality_score", "FLOAT DEFAULT 0.0")
                add_col_if_missing("products", "price_verified_at", "DATETIME")
                add_col_if_missing("products", "image_verified_at", "DATETIME")
                add_col_if_missing("products", "price_verification_status", "VARCHAR(30) DEFAULT 'unverified'")
                add_col_if_missing("products", "data_source", "VARCHAR(50) DEFAULT 'seed'")

                # prices table additions
                add_col_if_missing("prices", "verification_status", "VARCHAR(30) DEFAULT 'unverified'")
                add_col_if_missing("prices", "verified_at", "DATETIME")
                add_col_if_missing("prices", "source_method", "VARCHAR(50)")
                add_col_if_missing("prices", "confidence_score", "FLOAT DEFAULT 0.0")
                add_col_if_missing("prices", "parser_version", "VARCHAR(50)")
                add_col_if_missing("prices", "failure_reason", "VARCHAR(500)")

                # marketplace_offers table additions
                add_col_if_missing("marketplace_offers", "verification_status", "VARCHAR(30) DEFAULT 'unverified'")
                add_col_if_missing("marketplace_offers", "verified_at", "DATETIME")
                add_col_if_missing("marketplace_offers", "source_method", "VARCHAR(50)")
                add_col_if_missing("marketplace_offers", "confidence_score", "FLOAT DEFAULT 0.0")
                add_col_if_missing("marketplace_offers", "parser_version", "VARCHAR(50)")
                add_col_if_missing("marketplace_offers", "failure_reason", "VARCHAR(500)")
                add_col_if_missing("marketplace_offers", "shipping_cost_verified", "BOOLEAN DEFAULT 0")

                # product_images table additions
                add_col_if_missing("product_images", "http_status", "INTEGER")
                add_col_if_missing("product_images", "content_type", "VARCHAR(100)")
                add_col_if_missing("product_images", "image_width", "INTEGER")
                add_col_if_missing("product_images", "image_height", "INTEGER")
                add_col_if_missing("product_images", "image_hash", "VARCHAR(64)")
                add_col_if_missing("product_images", "verification_status", "VARCHAR(30) DEFAULT 'unverified'")
                add_col_if_missing("product_images", "verified_at", "DATETIME")
                add_col_if_missing("product_images", "failure_reason", "VARCHAR(500)")

        except Exception as e:
            print(f"[Warning] Table migration warning: {e}")

    # Seed default data freshness config
    try:
        from data_freshness import seed_freshness_config
        db = SessionLocal()
        try:
            seed_freshness_config(db)
        finally:
            db.close()
    except Exception as e:
        print(f"[Warning] Data freshness seeding warning: {e}")


