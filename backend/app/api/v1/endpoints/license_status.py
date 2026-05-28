from fastapi import APIRouter

from app.core.license import LicenseStatus, get_license_state

router = APIRouter()


@router.get("/admin/license/status")
async def license_status() -> dict:
    state = get_license_state()
    doc = state.document

    response: dict = {
        "status": state.status.value,
        "message": state.message,
        "bookings_allowed": state.bookings_allowed,
    }

    if state.status == LicenseStatus.MISSING:
        response["demo_mode"] = True
        response["demo_limits"] = {
            "max_bookings": state.DEMO_MAX_BOOKINGS,
            "current_bookings": state.demo_booking_count,
            "max_staff": state.DEMO_MAX_STAFF,
            "current_staff": state.demo_staff_count,
            "max_services": state.DEMO_MAX_SERVICES,
            "current_services": state.demo_service_count,
            "max_days": state.DEMO_MAX_DAYS,
        }

    if doc:
        response["license"] = {
            "license_id": doc.license_id,
            "edition": doc.edition.value,
            "expires_at": doc.expires_at.isoformat() if doc.expires_at else None,
            "grace_until": doc.grace_until.isoformat() if doc.grace_until else None,
            "max_staff": doc.max_staff,
            "max_services": doc.max_services,
        }

    return response
