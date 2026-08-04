from fastapi import APIRouter
from app.api.v1.endpoints import health, version, auth

api_v1_router = APIRouter()

api_v1_router.include_router(health.router, prefix="/health", tags=["Health"])
api_v1_router.include_router(version.router, prefix="/version", tags=["Version"])
api_v1_router.include_router(auth.router, prefix="/auth", tags=["Auth Foundation"])
