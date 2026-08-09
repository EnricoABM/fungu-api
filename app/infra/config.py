from dotenv import load_dotenv
from pathlib import Path

import os

load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env")

class Settings:
    DATABASE_URL = os.getenv("DATABASE_URL")