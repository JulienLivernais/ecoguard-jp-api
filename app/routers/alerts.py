from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.alert import Alert
from app.schemas.alert import AlertResponse

router = APIRouter()

@router.get("/alerts", response_model=list[AlertResponse])
def get_alerts(city: str = None, db: Session = Depends(get_db)):
    query = db.query(Alert).order_by(Alert.timestamp.desc())
    if city:
        query = query.filter(Alert.city == city)
    return query.limit(50).all()

