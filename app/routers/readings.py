from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.sensor_reading import SensorReading
from app.schemas.reading import ReadingResponse

router = APIRouter()

@router.get("/readings", response_model=list[ReadingResponse])
def get_readings(db: Session = Depends(get_db)):
    readings = db.query(SensorReading).order_by(SensorReading.timestamp.desc()).limit(50).all()
    return readings



