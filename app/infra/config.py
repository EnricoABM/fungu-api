from dotenv import load_dotenv
from pathlib import Path

import os

load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env")

class Settings:
    DATABASE_URL = os.getenv("DATABASE_URL", "")

    SECRET_KEY = os.getenv("SECRET_KEY", "")
    ALGORITHM = os.getenv("ALGORITHM", "")
    ACCESS_TOKEN_EXPIRE_MINUTES = float(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", ""))
    REFRESH_TOKEN_EXPIRE_MINUTES = float(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES", ""))