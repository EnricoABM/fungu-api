from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm 
from sqlalchemy.orm import Session

from app.api.dependencies import verify_access_token, auth_service, verify_refresh_token
from app.api.schemas.auth_schemas import LoginSchema 
from app.services.auth_service import AuthService
router = APIRouter()

@router.post("/login")
async def login(schema: LoginSchema, service: AuthService = Depends(auth_service)):
    try:
        access_token, refresh_token = service.login(email=schema.email, password=schema.password)
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Credenciais Inválidas")

@router.post("/login-form")
async def login_form(schema: OAuth2PasswordRequestForm = Depends(), service: AuthService = Depends(auth_service)):
    try:
        access_token, refresh_token = service.login(email=schema.username, password=schema.password)
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Credenciais Inválidas")

@router.get("/refresh")
async def use_refresh(user_id: int = Depends(verify_refresh_token), service: AuthService = Depends(auth_service)):
    try:
        access_token = service.generate_access_token(user_id)
        return {
            "access_token": access_token,
            "token_type": "Bearer"
        }
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))