from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found in environment variables. Check your .env file.")

# Create synchronous engine (compatible with Neon PostgreSQL + psycopg2)
engine = create_engine(
    DATABASE_URL,
    echo=bool(os.getenv("DEBUG", "False")),
    pool_pre_ping=True,       # Verify connections before use (important for Neon serverless)
    pool_recycle=300,          # Recycle connections every 5 minutes
    pool_size=5,
    max_overflow=10,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dependency: yields a database session and ensures it is closed after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables defined in models.py."""
    from models import Base
    Base.metadata.create_all(bind=engine)
    print("[OK] Database tables created successfully.")
