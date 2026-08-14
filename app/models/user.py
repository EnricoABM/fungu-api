from app.infra.database import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String

class User(Base):
    __tablename__ = "user_tb"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(), nullable=False)

    telegram_chat_id: Mapped[str] = mapped_column(String(), nullable=True)
    alert_email: Mapped[str] = mapped_column(String(), nullable=True)

    def __init__(self, email: str, password: str):
        self.email = email
        self.password_hash = password
        self.telegram_chat_id = None
        self.alert_email = None
