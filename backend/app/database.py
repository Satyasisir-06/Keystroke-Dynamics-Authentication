"""
KeyAuth - Database connection module
SQLAlchemy engine, session, and base — supports PostgreSQL (Supabase) and SQLite
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Build engine kwargs based on database type
connect_args = {}
engine_kwargs = {"echo": False}

if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
else:
    # PostgreSQL connection pool settings (optimized for serverless)
    engine_kwargs.update({
        "pool_size": 5,
        "max_overflow": 10,
        "pool_timeout": 30,
        "pool_recycle": 300,  # Recycle connections every 5 min
        "pool_pre_ping": True,  # Verify connections before use
    })

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    **engine_kwargs,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

_db_initialized = False


def get_db():
    """Dependency: yields a database session per request."""
    # Ensure tables exist (critical for Vercel serverless cold starts)
    global _db_initialized
    if not _db_initialized:
        init_db()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables (idempotent)."""
    global _db_initialized
    Base.metadata.create_all(bind=engine)
    _db_initialized = True
