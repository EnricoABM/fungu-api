from app.infra.database import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime
from datetime import datetime

class Measurement(Base):
    __tablename__ = "measurement_tb"

    id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True
    )

    measured_at: Mapped[datetime] = mapped_column(
        DateTime(), nullable=False
    )

    variable: Mapped[str] = mapped_column(
        String(), nullable=False
    )

    value: Mapped[str] = mapped_column(
        String(), nullable=False
    )

    def __init__(self, measured_at: datetime, variable: str, value: str):
        self.measured_at = measured_at
        self.variable = variable
        self.value = value