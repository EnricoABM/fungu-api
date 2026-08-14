from pydantic import BaseModel
from typing import Optional

class RegisterSchema(BaseModel):
    email: str
    password: str

    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    id: int
    email: str
    telegram_chat_id: Optional[str] = None
    alert_email: Optional[str] = None

    class Config:
        from_attributes = True