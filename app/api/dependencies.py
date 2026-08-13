from fastapi import Depends, HTTPException
from sqlalchemy.orm import sessionmaker, Session

from app.infra.security import oauth2_schema
from app.infra.database import LocalSession
from app.services.auth_service import AuthService
from app.services.device_service import DeviceService

def get_session():
    """Cria a sessão de banco de dados para serem usadas como dependencias"""
    try: 
        session = LocalSession()
        yield session
    finally:
        session.close() 

def auth_service(session: Session = Depends(get_session)):
    """Cria um objeto da classe AuthService"""
    return AuthService(session) 

def device_service(session: Session = Depends(get_session)):
    """Cria um objeto da classe DeviceService"""
    return DeviceService(session)

def verify_access_token(token: str = Depends(oauth2_schema), service: AuthService = Depends(auth_service)):
    """Verifica o acess token enviado em rotas protegidas"""
    try:
        user_id = service.verify_token(token)
        return user_id
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

def verify_refresh_token(token: str, service: AuthService = Depends(auth_service)):
    """Verifica o refresh token enviado pelo usuário"""
    try:
        user_id = service.verify_refresh_token(token)
        return user_id
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))