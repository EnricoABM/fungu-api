import json
from datetime import datetime, timezone, timedelta

from sqlalchemy.orm import Session

from app.models.measurement import Measurement
from app.infra.config import Settings

class MqttService:
    def __init__(self, session: Session):
        self._session = session

    def process(self, topic: str, payload: str):
        print(topic)

        info = json.loads(payload)

        for variable, value in info.items():
            measurement = Measurement(
                measured_at=datetime.now(timezone(timedelta(hours=-3))),
                variable=variable,
                value=value
            )

            print(f"[{variable}]: '{value}'")
            self._session.add(measurement)
        