from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps.auth import get_current_user
from app.core.security import hash_password, verify_password
from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.user import LoginRequest, UserCreate, UserRead

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/setup", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def setup_first_user(data: UserCreate, db: AsyncSession = Depends(get_db)) -> User:
    """Create the first owner user. Returns 409 if any user already exists."""
    count = await db.scalar(select(func.count()).select_from(User))
    if (count or 0) > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Setup already completed. An owner account already exists.",
        )
    user = User(
        email=data.email,
        password_hash=hash_password(data.password),
        display_name=data.display_name,
        role=UserRole.OWNER,
        is_active=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.post("/login", response_model=UserRead)
async def login(
    data: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> User:
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is inactive.")
    request.session["user_id"] = str(user.id)
    return user


@router.post("/logout")
async def logout(request: Request) -> dict:
    request.session.clear()
    return {"detail": "Logged out."}


@router.get("/me", response_model=UserRead)
async def me(current_user: User = Depends(get_current_user)) -> User:
    return current_user
