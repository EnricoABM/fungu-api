from typing import Any

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, String

from app.infra.database import Base

class Master(Base):
    __tablename__ = "master_tb"

    mac: Mapped[str] = mapped_column(
        primary_key=True
    )

    def __init__(self, mac: str):
        self.mac = mac

class Slave(Base):
    __tablename__ = "slave_tb"

    mac: Mapped[str] = mapped_column(
        String(), primary_key=True
    )

    master: Mapped[str] = mapped_column(
        ForeignKey("master_tb.mac"), nullable=True
    )

    def __init__(self, mac: str, master: str):
        self.mac = mac
        self.master = master