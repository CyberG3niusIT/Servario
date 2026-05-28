import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditActorType, AuditLog


async def log(
    db: AsyncSession,
    action: str,
    entity_type: str,
    entity_id: uuid.UUID | None = None,
    actor_type: AuditActorType = AuditActorType.SYSTEM,
    actor_id: uuid.UUID | None = None,
    changes: dict[str, Any] | None = None,
) -> None:
    entry = AuditLog(
        actor_type=actor_type,
        actor_id=actor_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        changes_json=changes,
        created_at=datetime.now(timezone.utc),
    )
    db.add(entry)
    # Caller is responsible for committing the transaction.
