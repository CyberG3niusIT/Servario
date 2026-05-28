from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.license import get_license_state
from app.db.session import get_db

router = APIRouter()


@router.get("/health")
async def health(db: AsyncSession = Depends(get_db)) -> dict:
    db_status = "connected"
    try:
        await db.execute(text("SELECT 1"))
    except Exception:
        db_status = "unavailable"

    state = get_license_state()
    return {
        "status": "ok" if db_status == "connected" else "degraded",
        "version": "0.1.0-dev",
        "database": db_status,
        "license_status": state.status.value,
        "license_message": state.message,
    }
