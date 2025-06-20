from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://taskuser:taskpass@localhost:5432/taskdb")

engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800  # Recycle connections after 30 minutes
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Use declarative_base from sqlalchemy.orm for SQLAlchemy 2.0 compatibility
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
