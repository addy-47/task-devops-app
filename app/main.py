from fastapi import FastAPI, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List
import logging
import os

# Try both import styles to support both Docker and local testing
try:
    # For local testing (app is a package)
    from app import models, database
    from app.database import get_db
except ImportError:
    # For Docker container (app is the working directory)
    import models
    import database
    from database import get_db

from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI instance at module level
api = FastAPI(title="Task Management API", version="1.0.0")

# Security headers middleware
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        return response

# Add security headers and CORS middleware
api.add_middleware(SecurityHeadersMiddleware)
api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict based on your requirements in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables if not in test environment
if os.getenv("ENVIRONMENT") != "test":
    try:
        models.Base.metadata.create_all(bind=database.engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")

# Health check endpoint
@api.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {"status": "healthy", "service": "task-api"}

# Create a new task
@api.post("/tasks/", status_code=status.HTTP_201_CREATED)
async def create_task(title: str, description: str = "", db: Session = Depends(get_db)):
    """Create a new task"""
    try:
        db_task = models.Task(title=title, description=description)
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        return db_task
    except Exception as e:
        logger.error(f"Error creating task: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Get all tasks
@api.get("/tasks/")
async def get_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all tasks with pagination"""
    try:
        tasks = db.query(models.Task).offset(skip).limit(limit).all()
        return [{"id": task.id, "title": task.title, "description": task.description, "completed": task.completed} for task in tasks]
    except Exception as e:
        logger.error(f"Error retrieving tasks: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Get a specific task by ID
@api.get("/tasks/{task_id}")
async def get_task(task_id: int, db: Session = Depends(get_db)):
    """Get a specific task by ID"""
    try:
        task = db.query(models.Task).filter(models.Task.id == task_id).first()
        if task is None:
            raise HTTPException(status_code=404, detail="Task not found")
        return {"id": task.id, "title": task.title, "description": task.description, "completed": task.completed}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving task: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Update a task
@api.put("/tasks/{task_id}")
async def update_task(
    task_id: int, 
    title: str | None = None, 
    description: str | None = None, 
    completed: bool | None = None,
    db: Session = Depends(get_db)
):
    """Update a task"""
    try:
        task = db.query(models.Task).filter(models.Task.id == task_id).first()
        if task is None:
            raise HTTPException(status_code=404, detail="Task not found")
        
        if title is not None:
            task.title = title
        if description is not None:
            task.description = description
        if completed is not None:
            task.completed = completed
            
        db.commit()
        db.refresh(task)
        return {"id": task.id, "title": task.title, "description": task.description, "completed": task.completed}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating task: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Delete a task
@api.delete("/tasks/{task_id}")
async def delete_task(task_id: int, db: Session = Depends(get_db)):
    """Delete a task"""
    try:
        task = db.query(models.Task).filter(models.Task.id == task_id).first()
        if task is None:
            raise HTTPException(status_code=404, detail="Task not found")
        
        db.delete(task)
        db.commit()
        return {"message": "Task deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting task: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Metrics endpoint for monitoring
@api.get("/metrics")
async def metrics():
    """Get application metrics for monitoring"""
    return {
        "total_tasks": get_task_count(),
        "service_status": "running"
    }

def get_task_count():
    """Helper function for metrics"""
    try:
        with database.SessionLocal() as db:
            return db.query(models.Task).count()
    except:
        return 0

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(api, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
