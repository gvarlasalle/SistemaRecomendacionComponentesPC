from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db

router = APIRouter()


@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    status = {"status": "healthy", "database": "unknown"}
    try:
        db.execute(text("SELECT 1"))
        status["database"] = "connected"
    except:
        status["database"] = "disconnected"
        status["status"] = "unhealthy"
    return status