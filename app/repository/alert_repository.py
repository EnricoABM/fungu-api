from sqlalchemy.orm import Session

from app.models.alert import AlertConfig


class AlertRepository:
    session: Session

    def __init__(self, session: Session):
        self.session = session

    def find_by_user(self, user_id: int):
        return self.session.query(AlertConfig).filter(AlertConfig.user_id == user_id).all()