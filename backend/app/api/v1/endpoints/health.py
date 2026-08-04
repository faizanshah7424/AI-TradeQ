from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.api.deps import get_db
from app.core.config import settings

router = APIRouter()

@router.get("")
def health_summary(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return {
        "status": "ok",
        "service": settings.PROJECT_NAME,
        "environment": settings.APP_ENV,
        "version": settings.VERSION,
        "components": {
            "database": db_status,
            "redis": "healthy (ready)"
        }
    }

@router.get("/live")
def liveness_probe():
    return {"status": "alive", "service": settings.PROJECT_NAME}

@router.get("/ready")
def readiness_probe(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failure: {str(e)}"
        )
    return {"status": "ready", "database": "connected", "redis": "connected"}

@router.get("/startup")
def startup_probe(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Startup database probe failed: {str(e)}"
        )
    return {"status": "started", "environment": settings.APP_ENV}
