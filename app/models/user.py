from app.infra.database import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String

class User(Base):
    __tablename__ = "user_tb"

    id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True
    )

    email: Mapped[str] = mapped_column(
        String(), unique=True, nullable=False
    )

    password_hash: Mapped[str] = mapped_column(
        String(), nullable=False
    )