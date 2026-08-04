from fastapi import APIRouter
from app.schemas.version import VersionResponse
from app.core.config import settings

router = APIRouter()

@router.get("", response_model=VersionResponse)
def get_version():
    return VersionResponse(
        version=settings.VERSION,
        environment="development",
        build="0.1.0-bootstrap"
    )
