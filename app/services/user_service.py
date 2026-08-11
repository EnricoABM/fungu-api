from sqlalchemy.orm import Session

from app.models.user import User
from app.infra.security import bcrypt_context

class UserService:

    def __init__(self, session: Session):
        self._session = session

    def register(self, email: str, password: str) -> User:
        user = self._session.query(User).filter(User.email == email).first()
        
        if user:
            raise ValueError("E-mail inválido")
        
        encrypted_password = bcrypt_context.hash(password)

        user = User(email, encrypted_password)
        self._session.add(user)
        self._session.commit()
        return user