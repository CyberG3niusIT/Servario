from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.license import get_or_create_instance_id, initialize_license, LicenseStatus

settings = get_settings()
DATA_DIR = Path("/data")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Resolve instance ID
    instance_id = get_or_create_instance_id(
        configured_id=settings.servario_instance_id,
        data_dir=DATA_DIR,
    )
    app.state.instance_id = instance_id

    # Validate license at startup
    state = initialize_license(
        license_key=settings.servario_license_key,
        grace_days=settings.servario_license_offline_grace_days,
        data_dir=DATA_DIR,
    )

    status_label = state.status.value.upper()
    print(f"[servario] License status: {status_label} — {state.message}")

    if state.status == LicenseStatus.INVALID:
        print("[servario] WARNING: License is invalid. New bookings are blocked.")
    elif state.status == LicenseStatus.MISSING:
        print("[servario] Running in Demo/Eval mode.")

    yield


app = FastAPI(
    title="Servario",
    version="0.1.0-dev",
    description="Self-hosted service scheduling platform",
    lifespan=lifespan,
    docs_url="/api/docs" if settings.is_development else None,
    redoc_url="/api/redoc" if settings.is_development else None,
)

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.secret_key,
    session_cookie="servario_session",
    max_age=86400 * 14,  # 14 days
    same_site="lax",
    https_only=not settings.is_development,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
