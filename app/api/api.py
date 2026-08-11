from fastapi import APIRouter
from app.api.endpoints import auth_router, user_router

api_router = APIRouter()

api_router.include_router(user_router.router, prefix="/users", tags=["Usuários"])
api_router.include_router(auth_router.router, prefix="/auth", tags=["Autenticação"])