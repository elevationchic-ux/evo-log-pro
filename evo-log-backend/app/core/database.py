"""
Database configuration and session management.
Dialect-aware: PostgreSQL with QueuePool for production multi-tenant concurrency,
SQLite with WAL mode for development. Zero "database is locked" errors.
"""
import logging
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import QueuePool, StaticPool
from app.core.config import settings

logger = logging.getLogger(__name__)

DATABASE_URL: str = settings.DATABASE_URL
_is_sqlite = DATABASE_URL.startswith("sqlite")


def _build_engine():
    """
    Build a dialect-aware SQLAlchemy engine.
    - PostgreSQL: QueuePool with pool_size=20, max_overflow=40, pool_pre_ping=True, pool_recycle=1800.
    - SQLite: StaticPool (single-connection in-memory for tests) OR
              QueuePool-compat connect_args with WAL journal for on-disk dev usage.
    """
    if _is_sqlite:
        logger.info("DATABASE: Using SQLite engine with WAL mode (dev/test)")
        # Use connect_args to avoid threading issues; StaticPool only for :memory:
        if ":memory:" in DATABASE_URL:
            engine = create_engine(
                DATABASE_URL,
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
                echo=settings.DEBUG,
            )
        else:
            engine = create_engine(
                DATABASE_URL,
                connect_args={"check_same_thread": False, "timeout": 30},
                echo=settings.DEBUG,
            )

        # Activate WAL journal mode and optimise SQLite for concurrent readers
        @event.listens_for(engine, "connect")
        def _set_sqlite_pragmas(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.execute("PRAGMA cache_size=-64000")   # 64 MB page cache
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.execute("PRAGMA temp_store=MEMORY")
            cursor.close()

        return engine

    else:
        # PostgreSQL / other dialects — full production pool
        logger.info("DATABASE: Using PostgreSQL engine with QueuePool (production)")
        return create_engine(
            DATABASE_URL,
            poolclass=QueuePool,
            pool_size=settings.DATABASE_POOL_SIZE,
            max_overflow=settings.DATABASE_MAX_OVERFLOW,
            pool_timeout=30,
            pool_recycle=1800,            # recycle connections after 30 min
            pool_pre_ping=True,           # validate connections before use
            echo=settings.DEBUG,
        )


# Singleton engine
engine = _build_engine()

# Session factory — autoflush=False to avoid premature DB writes mid-request
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all ORM models
Base = declarative_base()


def get_db():
    """
    FastAPI dependency — yields a database session scoped to a single HTTP request.
    Always closes the session (and returns it to the pool) even on error.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()