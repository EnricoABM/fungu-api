from datetime import datetime

from pydantic import BaseModel, field_validator


class MeasurementResponse(BaseModel):
    id: int
    measured_at: datetime
    variable: str
    value: float

    class Config:
        from_attributes = True

    @field_validator("value", mode="before")
    @classmethod
    def cast_value_to_float(cls, v):
        if isinstance(v, str):
            return float(v)
        return v


class MeasurementListResponse(BaseModel):
    measurements: list[MeasurementResponse]
    total: int
    page: int
    page_size: int


class LatestMeasurementsResponse(BaseModel):
    variable: str
    value: float
    measured_at: datetime

    class Config:
        from_attributes = True

    @field_validator("value", mode="before")
    @classmethod
    def cast_value_to_float(cls, v):
        if isinstance(v, str):
            return float(v)
        return v
