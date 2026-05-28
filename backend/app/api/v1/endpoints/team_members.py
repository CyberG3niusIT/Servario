import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps.auth import require_admin
from app.core.license import get_license_state, LicenseStatus
from app.db.session import get_db
from app.models.availability import AvailabilityException, AvailabilityRule
from app.models.service import ServiceTeamMember
from app.models.team_member import TeamMember
from app.models.user import User
from app.schemas.team_member import (
    AvailabilityExceptionCreate,
    AvailabilityExceptionRead,
    AvailabilityRuleCreate,
    AvailabilityRuleRead,
    TeamMemberCreate,
    TeamMemberRead,
    TeamMemberUpdate,
)

router = APIRouter(prefix="/api/admin/team-members", tags=["admin-team-members"])


@router.get("", response_model=list[TeamMemberRead])
async def list_team_members(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> list[TeamMember]:
    result = await db.execute(select(TeamMember).order_by(TeamMember.display_name))
    return result.scalars().all()


@router.post("", response_model=TeamMemberRead, status_code=status.HTTP_201_CREATED)
async def create_team_member(
    data: TeamMemberCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> TeamMember:
    state = get_license_state()
    if state.status == LicenseStatus.MISSING:
        result = await db.execute(select(TeamMember))
        count = len(result.scalars().all())
        if not state.check_staff_limit(count):
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"Demo mode limit reached ({state.DEMO_MAX_STAFF} staff). A license is required.",
            )

    member = TeamMember(
        display_name=data.display_name,
        email=data.email,
        bio=data.bio,
        is_active=data.is_active,
    )
    db.add(member)
    await db.flush()

    for svc_id in data.service_ids:
        db.add(ServiceTeamMember(service_id=svc_id, team_member_id=member.id))

    await db.commit()
    await db.refresh(member)
    return member


@router.get("/{member_id}", response_model=TeamMemberRead)
async def get_team_member(
    member_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> TeamMember:
    member = await db.get(TeamMember, member_id)
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team member not found.")
    return member


@router.patch("/{member_id}", response_model=TeamMemberRead)
async def update_team_member(
    member_id: uuid.UUID,
    data: TeamMemberUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> TeamMember:
    member = await db.get(TeamMember, member_id)
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team member not found.")

    for field, value in data.model_dump(exclude_unset=True, exclude={"service_ids"}).items():
        setattr(member, field, value)

    if data.service_ids is not None:
        await db.execute(
            delete(ServiceTeamMember).where(ServiceTeamMember.team_member_id == member_id)
        )
        for svc_id in data.service_ids:
            db.add(ServiceTeamMember(service_id=svc_id, team_member_id=member_id))

    await db.commit()
    await db.refresh(member)
    return member


# ── Availability rules ────────────────────────────────────────────────────────

@router.get("/{member_id}/availability-rules", response_model=list[AvailabilityRuleRead])
async def list_rules(
    member_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> list[AvailabilityRule]:
    result = await db.execute(
        select(AvailabilityRule)
        .where(AvailabilityRule.team_member_id == member_id)
        .order_by(AvailabilityRule.day_of_week)
    )
    return result.scalars().all()


@router.post(
    "/{member_id}/availability-rules",
    response_model=AvailabilityRuleRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_rule(
    member_id: uuid.UUID,
    data: AvailabilityRuleCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> AvailabilityRule:
    member = await db.get(TeamMember, member_id)
    if not member:
        raise HTTPException(status_code=404, detail="Team member not found.")
    rule = AvailabilityRule(team_member_id=member_id, **data.model_dump())
    db.add(rule)
    await db.commit()
    await db.refresh(rule)
    return rule


@router.delete("/{member_id}/availability-rules/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rule(
    member_id: uuid.UUID,
    rule_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> None:
    rule = await db.get(AvailabilityRule, rule_id)
    if not rule or rule.team_member_id != member_id:
        raise HTTPException(status_code=404, detail="Rule not found.")
    await db.delete(rule)
    await db.commit()


# ── Availability exceptions ───────────────────────────────────────────────────

@router.post(
    "/{member_id}/availability-exceptions",
    response_model=AvailabilityExceptionRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_exception(
    member_id: uuid.UUID,
    data: AvailabilityExceptionCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> AvailabilityException:
    member = await db.get(TeamMember, member_id)
    if not member:
        raise HTTPException(status_code=404, detail="Team member not found.")
    exc = AvailabilityException(team_member_id=member_id, **data.model_dump())
    db.add(exc)
    await db.commit()
    await db.refresh(exc)
    return exc
