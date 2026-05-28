"""Admin-Endpunkte für Instanz-Einstellungen (SMTP, Geschäftsdaten, Buchungsseite)."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps.auth import get_current_user
from app.db.session import get_db
from app.models.settings import InstanceSettings
from app.models.user import User
from app.schemas.settings import InstanceSettingsRead, InstanceSettingsUpdate

router = APIRouter(prefix="/api/admin/settings", tags=["admin-settings"])


async def _get_or_create(db: AsyncSession) -> InstanceSettings:
    row = await db.get(InstanceSettings, 1)
    if not row:
        row = InstanceSettings(id=1)
        db.add(row)
        await db.flush()
    return row


@router.get("", response_model=InstanceSettingsRead)
async def get_settings(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> InstanceSettingsRead:
    row = await _get_or_create(db)
    return InstanceSettingsRead(
        business_name=row.business_name,
        business_email=row.business_email,
        business_phone=row.business_phone,
        business_address=row.business_address,
        booking_page_title=row.booking_page_title,
        booking_page_description=row.booking_page_description,
        timezone=row.timezone,
        smtp_host=row.smtp_host,
        smtp_port=row.smtp_port,
        smtp_user=row.smtp_user,
        smtp_configured=bool(row.smtp_host and row.smtp_user and row.smtp_password_encrypted),
    )


@router.patch("", response_model=InstanceSettingsRead)
async def update_settings(
    data: InstanceSettingsUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> InstanceSettingsRead:
    row = await _get_or_create(db)
    update = data.model_dump(exclude_unset=True)

    # Passwort separat behandeln — wird im Klartext im verschlüsselten Feld gespeichert
    # (Verschlüsselung kann später mit Fernet ergänzt werden)
    if "smtp_password" in update:
        row.smtp_password_encrypted = update.pop("smtp_password") or None

    for field, value in update.items():
        setattr(row, field, value)

    await db.commit()
    await db.refresh(row)
    return InstanceSettingsRead(
        business_name=row.business_name,
        business_email=row.business_email,
        business_phone=row.business_phone,
        business_address=row.business_address,
        booking_page_title=row.booking_page_title,
        booking_page_description=row.booking_page_description,
        timezone=row.timezone,
        smtp_host=row.smtp_host,
        smtp_port=row.smtp_port,
        smtp_user=row.smtp_user,
        smtp_configured=bool(row.smtp_host and row.smtp_user and row.smtp_password_encrypted),
    )
