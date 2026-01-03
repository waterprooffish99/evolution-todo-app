"""
Database connection setup for Neon Serverless PostgreSQL.

This module configures the SQLModel engine with connection pooling
and provides FastAPI dependencies for database sessions.
"""

from sqlmodel import create_engine, SQLModel, Session
import os
from dotenv import load_dotenv

load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")

# Create engine with connection pooling for Neon
engine = create_engine(
    DATABASE_URL,
    echo=True if os.getenv("ENVIRONMENT") == "development" else False,
    pool_pre_ping=True,  # Verify connections before using (handles stale connections)
    pool_size=5,         # Number of persistent connections
    max_overflow=10      # Additional connections when pool is full (total: 15)
)


def create_db_and_tables():
    """
    Create all database tables from SQLModel metadata.

    Note: In production, use Alembic migrations instead of this function.
    This is primarily for development and testing.
    """
    SQLModel.metadata.create_all(engine)


def get_session():
    """
    FastAPI dependency to get a database session.

    Yields a SQLModel Session that will be automatically closed after the request.

    Usage in FastAPI endpoint:
        @app.get("/endpoint")
        async def endpoint(db: Session = Depends(get_session)):
            # Use db here
            pass
    """
    with Session(engine) as session:
        yield session
