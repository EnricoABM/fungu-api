from app.infra.database import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, ForeignKey, Float

class AlertConfig(Base):
    __tablename__ = "alert_config_tb"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user_tb.id"), nullable=False)
    variable: Mapped[str] = mapped_column(String(), nullable=False) 
    condition: Mapped[str] = mapped_column(String(), nullable=False) # Aceitará ">", "<" ou "=="
    threshold: Mapped[float] = mapped_column(Float(), nullable=False)

    def __init__(self, user_id: int, variable: str, condition: str, threshold: float):
        self.user_id = user_id
        self.variable = variable
        self.condition = condition
        self.threshold = threshold
