from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.dependencies import get_session, verify_access_token
from app.api.schemas.alert_schemas import ContactUpdateSchema
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
        raise HTTPException(status_code=400, detail=str(e)) 
# ...
@router.patch("/contacts")
async def update_contacts(schema: ContactUpdateSchema, user_id: int = Depends(verify_access_token), session: Session = Depends(get_session)):
    try:
        service = UserService(session)
        service.update_contacts(user_id, schema.telegram_chat_id, schema.alert_email)
        return {"mensagem": "Contatos atualizados com sucesso."}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
