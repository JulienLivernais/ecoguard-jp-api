from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class BulletinBase(BaseModel):
    date_start: datetime = Field(...)
    date_end: datetime = Field(...)


class BulletinCreate(BulletinBase):
    pass


class BulletinResponse(BulletinBase):
    id: int
    bulletin: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

