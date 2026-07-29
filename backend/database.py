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
    """Create all tables. Called on application startup."""
    import models  # noqa: F401 - Import to register models with Base
    Base.metadata.create_all(bind=engine)
