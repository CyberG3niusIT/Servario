from fastapi import APIRouter

from app.api.v1.endpoints import (
    admin_bookings,
    auth,
    health,
    license_status,
    public_booking,
    services,
    team_members,
)

api_router = APIRouter()

api_router.include_router(health.router, tags=["health"])
api_router.include_router(license_status.router, prefix="/api", tags=["license"])
api_router.include_router(auth.router)
api_router.include_router(services.router)
api_router.include_router(team_members.router)
api_router.include_router(admin_bookings.router)
api_router.include_router(public_booking.router)
