from pydantic import BaseModel
from typing import Optional

class AlertCreateSchema(BaseModel):
    variable: str
    condition: str
    threshold: float

class ContactUpdateSchema(BaseModel):
    telegram_chat_id: Optional[str] = None
    alert_email: Optional[str] = None

class AlertResponse(BaseModel):
    id: int
    variable: str
    condition: str
    threshold: float

    class Config:
        from_attributes = True

class AlertListResponse(BaseModel):
    alerts: list[AlertResponse]
