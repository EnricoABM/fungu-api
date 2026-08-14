from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.dependencies import get_session, verify_access_token
from app.api.schemas.alert_schemas import AlertCreateSchema, AlertListResponse, AlertResponse
from app.models.alert import AlertConfig
from app.services.alert_service import AlertService

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

@router.get("")
async def list_alerts(user_id: int = Depends(verify_access_token), session: Session = Depends(get_session)):
    service = AlertService(session)
    alerts = service.list_alerts(user_id)
    return AlertListResponse(alerts=[AlertResponse(id=a.id, variable=a.variable, condition=a.condition, threshold=a.threshold) for a in alerts])
