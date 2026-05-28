from fastapi import APIRouter

from app.api.v1.endpoints import health, license_status

api_router = APIRouter()

api_router.include_router(health.router, tags=["health"])
api_router.include_router(license_status.router, prefix="/api", tags=["license"])
