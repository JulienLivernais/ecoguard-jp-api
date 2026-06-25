from pydantic import BaseModel, Field, ConfigDict
from app.models.alert import AlertType, AlertParameter
from datetime import datetime


class AlertBase(BaseModel):
    city: str = Field(...)
    timestamp: datetime = Field(...)
    alert_type: AlertType
    parameter: AlertParameter
    value: float | None = Field(None)
    threshold: float | None = Field(None)
    anomaly_score: float | None = Field(None)
    message: str = Field(...)


class AlertCreate(AlertBase):
    pass


class AlertResponse(AlertBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

