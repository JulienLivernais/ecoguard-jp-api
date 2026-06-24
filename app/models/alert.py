from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Text, Float
from app.core.database import Base
from sqlalchemy import DateTime
from datetime import datetime
import enum
from sqlalchemy import Enum as SAEnum


class AlertType(enum.Enum):
    spike = "spike"
    trend = "trend"


class AlertParameter(enum.Enum):
    aqi = "aqi"
    pm25 = "pm25"
    pm10 = "pm10"
    no2 = "no2"
    o3 = "o3"
    temperature = "temperature"
    humidity = "humidity"


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(primary_key=True)
    city: Mapped[str] = mapped_column(Text, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    alert_type: Mapped[AlertType] = mapped_column(SAEnum(AlertType), nullable=False)
    parameter: Mapped[AlertParameter] = mapped_column(SAEnum(AlertParameter), nullable=False)
    value: Mapped[float] = mapped_column(Float, nullable=True)
    threshold: Mapped[float] = mapped_column(Float, nullable=True)
    anomaly_score: Mapped[float] = mapped_column(Float, nullable=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)


