from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from app.models.measurement import Measurement


class MeasurementRepository:
    session: Session

    def __init__(self, session: Session):
        self.session = session

    def find_all(
        self,
        variable: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> Tuple[List[Measurement], int]:
        query = self.session.query(Measurement)

        if variable:
            query = query.filter(Measurement.variable == variable)
        if start_date:
            query = query.filter(Measurement.measured_at >= start_date)
        if end_date:
            query = query.filter(Measurement.measured_at <= end_date)

        total = query.count()

        measurements = (
            query.order_by(Measurement.measured_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        return measurements, total

    def find_latest_per_variable(self) -> List[Measurement]:
        variables = [
            row[0]
            for row in self.session.query(Measurement.variable).distinct().all()
        ]

        latest: List[Measurement] = []
        for variable in variables:
            measurement = (
                self.session.query(Measurement)
                .filter(Measurement.variable == variable)
                .order_by(Measurement.measured_at.desc())
                .first()
            )
            if measurement:
                latest.append(measurement)

        return latest
