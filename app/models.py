from sqlalchemy import Boolean, Column, Integer, String, DateTime
from sqlalchemy.sql import func

# Try both import styles to support both Docker and local testing
try:
    # For local testing (app is a package)
    from app.database import Base
except ImportError:
    # For Docker container (app is the working directory)
    from database import Base

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String, default="")
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
