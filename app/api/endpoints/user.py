from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_session
from app.models.user import User
from app.api.schemas.user_schemas import RegisterSchema 
from app.infra.security import bcrypt_context

router = APIRouter()

@router.post("/register")
async def register(schema: RegisterSchema, session: Session = Depends(get_session)):
    user = session.query(User).filter(User.email == schema.email).first()

    if user:
        return HTTPException(status_code=400, detail="E-mail inválido")

    encrypted_password = bcrypt_context.hash(schema.password)

    session.add(User(schema.email, encrypted_password))
    session.commit()
    return {"Registro": "Sucesso"}
