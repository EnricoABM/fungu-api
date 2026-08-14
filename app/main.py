# Comando de execução
# uvicorn main:app --reload

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from contextlib import asynccontextmanager

from app.api import api
from app.infra.database import Base, engine
from app.infra.mqtt.mqtt import MqttClient
from app.infra.config import Settings
from app.infra.mqtt.handler import MqttHandler

mqtt_client = MqttClient(
    broker_ip=Settings.MQTT_HOST,
    port=Settings.MQTT_PORT,
    topic=Settings.MQTT_TOPIC,
    handler=MqttHandler(),
    keepalive=Settings.MQTT_KEEPALIVE
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    mqtt_client.start_connection()
    yield
    mqtt_client.stop_connection()

app = FastAPI(
    lifespan=lifespan
) 

app.include_router(api.api_router)
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")