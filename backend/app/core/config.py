from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Database
    database_url: str

    # Application
    secret_key: str
    environment: str = "production"
    allowed_origins: list[str] = ["http://localhost:3000"]

    # License
    servario_license_key: str = ""
    servario_license_server_url: str = ""
    servario_instance_id: str = ""
    servario_license_offline_grace_days: int = 30

    # SMTP (optional at startup; configured via Admin UI)
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""

    @property
    def is_development(self) -> bool:
        return self.environment == "development"


@lru_cache
def get_settings() -> Settings:
    return Settings()
