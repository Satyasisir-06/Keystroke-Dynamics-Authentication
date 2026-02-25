"""
KeyAuth - Database connection module
SQLAlchemy engine, session, and base — supports PostgreSQL (Supabase) and SQLite
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Build engine kwargs based on database type
db_url = settings.DATABASE_URL
connect_args = {}
engine_kwargs = {"echo": False}

if db_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
else:
    # Force pg8000 driver for ALL PostgreSQL URLs (pure Python — no pg_config needed)
    # Handle all common URL formats: postgres://, postgresql://, postgresql+psycopg2://
    for prefix in [
        "postgresql+psycopg2://",
        "postgresql+psycopg2binary://",
        "postgres://",
        "postgresql://",
    ]:
        if db_url.startswith(prefix):
            db_url = "postgresql+pg8000://" + db_url[len(prefix):]
            break

    # PostgreSQL connection pool settings (optimized for serverless)
    engine_kwargs.update({
        "pool_size": 3,
        "max_overflow": 5,
        "pool_timeout": 30,
        "pool_recycle": 300,
        "pool_pre_ping": True,
    })


engine = create_engine(
    db_url,
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
