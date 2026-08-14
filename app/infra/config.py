from dotenv import load_dotenv
from pathlib import Path

import os

load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env")

class Settings:
    # DATABASE
    DATABASE_URL = os.getenv("DATABASE_URL", "")

    # JWT
    SECRET_KEY = os.getenv("SECRET_KEY", "")
    ALGORITHM = os.getenv("ALGORITHM", "")
    ACCESS_TOKEN_EXPIRE_MINUTES = float(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", ""))
    REFRESH_TOKEN_EXPIRE_MINUTES = float(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES", ""))

    # MQTT
    MQTT_HOST = os.getenv("MQTT_HOST", "")
    MQTT_PORT = int(os.getenv("MQTT_PORT", ""))
    MQTT_CLIENT = os.getenv("MQTT_CLIENT", "")
    MQTT_KEEPALIVE = int(os.getenv("MQTT_KEEPALIVE", ""))
    MQTT_TOPIC = os.getenv("MQTT_TOPIC", "")

    # TIMEZONE
    TIMEZONE = os.getenv("TIMEZONE", "")

    # ALERTAS SMTP
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
    SMTP_USER = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

    # ALERTAS TELEGRAM
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
