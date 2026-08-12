from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.infra.config import Settings

engine = create_engine(
    Settings.DATABASE_URL,
    echo=True
)

LocalSession = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass


