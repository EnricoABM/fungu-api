from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_session, verify_access_token
from app.api.schemas.measurement_schemas import (
    LatestMeasurementsResponse,
    MeasurementListResponse,
)
from app.services.measurement_service import MeasurementService

router = APIRouter()


@router.get("")
async def list_measurements(
    variable: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    page: int = 1,
    page_size: int = 50,
    session: Session = Depends(get_session),
    user_id: int = Depends(verify_access_token),
) -> MeasurementListResponse:
    try:
        service = MeasurementService(session)
        return service.list_measurements(
            variable=variable,
            start_date=start_date,
            end_date=end_date,
            page=page,
            page_size=page_size,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/latest")
async def get_latest_measurements(
    session: Session = Depends(get_session),
    user_id: int = Depends(verify_access_token),
) -> List[LatestMeasurementsResponse]:
    try:
        service = MeasurementService(session)
        return service.get_latest_measurements()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))