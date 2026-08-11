from sqlalchemy.orm import Session

from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone

from app.infra.security import bcrypt_context 
from app.models.user import User
from app.infra.config import Settings

class AuthService:
    def __init__(self, session: Session):
        self._session = session

    # ========================================================
    #                       AUTENTICAÇÃO
    # ========================================================
    def login(self, email: str, password: str) -> tuple[str, str]:
        user = self._session.query(User).filter(User.email == email).first()
        if not user or not bcrypt_context.verify(password, user.password_hash):
            raise ValueError("Credenciais Inválidas")

        access_token = self.generate_access_token(user.id)
        refresh_token = self.generate_refresh_token(user.id)

        return (access_token, refresh_token)

    # ========================================================
    #                 VERIFICAÇÃO DE TOKEN
    # ========================================================
    def verify_token(self, token: str) -> int:
        try:
            info = jwt.decode(token, Settings.SECRET_KEY, Settings.ALGORITHM)
            user_id = info.get("sub")
            if user_id is None:
                raise ValueError("Token Inválido") 
            id = int(user_id)

        except (JWTError, ValueError):
            raise ValueError("Token Inválido")
        
        user = self._session.query(User).filter(User.id == id).first()
        if not user:
            raise ValueError("Acesso Negado")

        return user.id

    def verify_refresh_token(self, token: str) -> int:
        try:
            info = jwt.decode(token, Settings.SECRET_KEY, Settings.ALGORITHM)
            
            typ = info.get("typ")
            if typ != "refresh":
                raise ValueError("Token Inválido")

            user_id = info.get("sub")
            if user_id is None:
                raise ValueError("Token Inválido") 
            id = int(user_id)
        
        except (JWTError, ValueError):
            raise ValueError("Token Inválido")
                
        user = self._session.query(User).filter(User.id == id).first()

        if not user:
            raise ValueError("Acesso Negado")
        
        return user.id
    
    # ========================================================
    #                     GERAÇÃO DE TOKEN
    # ========================================================
    def generate_access_token(self, id: int):
        """Gera token de acesso JWT"""
        return self.__generate_token(id, timedelta(minutes=Settings.ACCESS_TOKEN_EXPIRE_MINUTES), "access")

    def generate_refresh_token(self, id: int):
        """Gera token de recuperação"""
        return self.__generate_token(id, timedelta(minutes=Settings.REFRESH_TOKEN_EXPIRE_MINUTES), "refresh")

    def __generate_token(self, id: int, duration: timedelta, type: str) -> str:
        """Gera token conforme identificador e duração"""
        expired_date = datetime.now(timezone.utc) + duration
        info = {
            "sub": str(id),
            "exp": expired_date,
            "typ": type
        }
        encoded_jwt = jwt.encode(info, Settings.SECRET_KEY, Settings.ALGORITHM)
        return encoded_jwt

    
            


