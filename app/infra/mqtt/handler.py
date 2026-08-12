from sqlalchemy.orm import Session

from app.infra.database import LocalSession
from app.services.mqtt_service import MqttService



class MqttHandler:
    def handle(self, message):
        topic = message.topic
        payload = message.payload.decode("utf-8")

        session: Session = LocalSession()
        try:
            service = MqttService(session)

            service.process(topic, payload)

            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()