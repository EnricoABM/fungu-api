from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.dependencies import get_session, verify_access_token
from app.api.schemas.alert_schemas import AlertCreateSchema
from app.models.alert import AlertConfig

router = APIRouter()

@router.post("/register")
async def create_alert(schema: AlertCreateSchema, user_id: int = Depends(verify_access_token), session: Session = Depends(get_session)):
    alert = AlertConfig(
        user_id=user_id,
        variable=schema.variable,
        condition=schema.condition,
        threshold=schema.threshold
    )
    session.add(alert)
    session.commit()
    return {"mensagem": "Alerta configurado."}
