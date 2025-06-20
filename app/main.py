from fastapi import FastAPI, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List
import logging
import os
from app import models, database
from app.database import get_db
import python_multipart

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI instance at module level
app = FastAPI(title="Task Management API", version="1.0.0")

# Create tables if not in test environment
if os.getenv("ENVIRONMENT") != "test":
    try:
        models.Base.metadata.create_all(bind=database.engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {"status": "healthy", "service": "task-api"}

# Metrics endpoint
@app.get("/metrics")
async def metrics():
    """Basic metrics endpoint for monitoring integration"""
    try:
        db = next(get_db())
        task_count = db.query(models.Task).count()
        db.close()
        return {
            "total_tasks": task_count,
            "service_status": "running"
        }
    except Exception as e:
        logger.error(f"Error getting metrics: {str(e)}")
        return {
            "total_tasks": 0,
            "service_status": "error"
        }

@app.post("/tasks/", status_code=status.HTTP_201_CREATED)
async def create_task(title: str, description: str = "", db: Session = Depends(get_db)):
    """Create a new task"""
    logger.info(f"Creating task: {title}")
    db_task = models.Task(title=title, description=description)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@app.get("/tasks/", response_model=List[dict])
async def get_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all tasks with pagination"""
    tasks = db.query(models.Task).offset(skip).limit(limit).all()
    return [{"id": t.id, "title": t.title, "description": t.description, "completed": t.completed} for t in tasks]

@app.get("/tasks/{task_id}")
async def get_task(task_id: int, db: Session = Depends(get_db)):
    """Get a specific task"""
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"id": task.id, "title": task.title, "description": task.description, "completed": task.completed}

@app.put("/tasks/{task_id}")
async def update_task(task_id: int, title: str = None, description: str = None,
                     completed: bool = None, db: Session = Depends(get_db)):
    """Update a task"""
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if title is not None:
        task.title = title
    if description is not None:
        task.description = description
    if completed is not None:
        task.completed = completed

    db.commit()
    logger.info(f"Updated task {task_id}")
    return {"id": task.id, "title": task.title, "description": task.description, "completed": task.completed}

@app.delete("/tasks/{task_id}")
async def delete_task(task_id: int, db: Session = Depends(get_db)):
    """Delete a task"""
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task)
    db.commit()
    logger.info(f"Deleted task {task_id}")
    return {"message": "Task deleted successfully"}

def get_task_count():
    """Helper function for metrics"""
    try:
        with database.SessionLocal() as db:
            return db.query(models.Task).count()
    except:
        return 0

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
