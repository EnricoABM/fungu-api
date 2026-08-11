from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_session
from app.api.schemas.user_schemas import RegisterSchema 
from app.services.user_service import UserService
router = APIRouter()

@router.post("/register")
async def register(schema: RegisterSchema, session: Session = Depends(get_session)):
    try:
        service = UserService(session)
        service.register(email=schema.email, password=schema.password)
        return {"mensagem": "cadastrado com sucesso"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=e)
