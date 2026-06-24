from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, Text, Float
from app.core.database import Base
from sqlalchemy import DateTime
from datetime import datetime


class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id: Mapped[int] = mapped_column(primary_key=True)
    city: Mapped[str] = mapped_column(Text, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    aqi: Mapped[int] = mapped_column(Integer, nullable=True)
    pm25: Mapped[float] = mapped_column(Float, nullable=True)
    pm10: Mapped[float] = mapped_column(Float, nullable=True)
    no2: Mapped[float] = mapped_column(Float, nullable=True)
    o3: Mapped[float] = mapped_column(Float, nullable=True)
    temperature: Mapped[float] = mapped_column(Float, nullable=True)
    humidity: Mapped[float] = mapped_column(Float, nullable=True)


