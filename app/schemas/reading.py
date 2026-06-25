from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class ReadingBase(BaseModel):
    city: str = Field(...)
    timestamp: datetime = Field(...)
    aqi: int = Field(...)
    pm25: float | None = Field(None)
    pm10: float | None = Field(None)
    no2: float | None = Field(None)
    o3: float | None = Field(None)
    temperature: float | None = Field(None)
    humidity: float | None = Field(None)


class ReadingCreate(ReadingBase):
    pass


class ReadingResponse(ReadingBase):
    id: int

    model_config = ConfigDict(from_attributes=True)








