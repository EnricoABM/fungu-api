from sqlalchemy.orm import Session

from app.repository.alert_repository import AlertRepository


class AlertService:
    repository: AlertRepository

    def __init__(self, session: Session):
        self.repository = AlertRepository(session)

    def list_alerts(self, user_id: int):
        return self.repository.find_by_user(user_id)