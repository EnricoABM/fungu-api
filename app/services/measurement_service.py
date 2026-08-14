from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from app.api.schemas.measurement_schemas import (
    LatestMeasurementsResponse,
    MeasurementListResponse,
    MeasurementResponse,
)
from app.repository.measurement_repository import MeasurementRepository


class MeasurementService:
    repository: MeasurementRepository

    def __init__(self, session: Session):
        self.repository = MeasurementRepository(session)

    def list_measurements(
        self,
        variable: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> MeasurementListResponse:
        measurements, total = self.repository.find_all(
            variable=variable,
            start_date=start_date,
            end_date=end_date,
            page=page,
            page_size=page_size,
        )

        return MeasurementListResponse(
            measurements=[
                MeasurementResponse.model_validate(m) for m in measurements
            ],
            total=total,
            page=page,
            page_size=page_size,
        )

    def get_latest_measurements(self) -> List[LatestMeasurementsResponse]:
        latest = self.repository.find_latest_per_variable()

        return [
            LatestMeasurementsResponse.model_validate(m) for m in latest
        ]