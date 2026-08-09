from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
from app.infra.config import Settings

engine = create_engine(
    Settings.DATABASE_URL,
    echo=True
    )

class Base(DeclarativeBase):
    pass


