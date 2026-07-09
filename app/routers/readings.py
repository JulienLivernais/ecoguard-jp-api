from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.sensor_reading import SensorReading
from app.schemas.reading import ReadingResponse

router = APIRouter()

@router.get("/readings", response_model=list[ReadingResponse])
def get_readings(city: str = None, db: Session = Depends(get_db)):
    query = db.query(SensorReading).order_by(SensorReading.timestamp.desc())
    if city:
        query = query.filter(SensorReading.city == city)
    return query.limit(50).all()






