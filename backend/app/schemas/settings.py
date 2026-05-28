from pydantic import BaseModel, EmailStr


class InstanceSettingsRead(BaseModel):
    business_name: str | None = None
    business_email: str | None = None
    business_phone: str | None = None
    business_address: str | None = None
    booking_page_title: str | None = None
    booking_page_description: str | None = None
    timezone: str = "UTC"
    smtp_host: str | None = None
    smtp_port: int | None = 587
    smtp_user: str | None = None
    smtp_configured: bool = False

    model_config = {"from_attributes": True}


class InstanceSettingsUpdate(BaseModel):
    business_name: str | None = None
    business_email: str | None = None
    business_phone: str | None = None
    business_address: str | None = None
    booking_page_title: str | None = None
    booking_page_description: str | None = None
    timezone: str | None = None
    smtp_host: str | None = None
    smtp_port: int | None = None
    smtp_user: str | None = None
    smtp_password: str | None = None
