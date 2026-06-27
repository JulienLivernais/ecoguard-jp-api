from worker.celery_app import app
from app.core.database import SessionLocal
from app.models.sensor_reading import SensorReading
from ml.anomaly_detector import AnomalyDetector
from app.models.alert import Alert, AlertType, AlertParameter
from datetime import datetime, timezone

ANOMALY_THRESHOLD = 0.7

@app.task
def run_anomaly_detection(city: str):
    db = SessionLocal()
    try:
        readings = (
            db.query(SensorReading)
            .filter(SensorReading.city == city)
            .order_by(SensorReading.timestamp.desc())
            .limit(24)
            .all()
        )
        if len(readings) < 24:
            return

        aqi_values = [r.aqi for r in reversed(readings)]
        model = AnomalyDetector()
        anomaly_score = model.predict(aqi_values)

        if anomaly_score > ANOMALY_THRESHOLD:
            alert = Alert(
                city=city,
                timestamp=datetime.now(timezone.utc),
                alert_type=AlertType.trend,
                parameter=AlertParameter.aqi,
                value=aqi_values[-1],
                anomaly_score=anomaly_score,
                message=f"AQI anomaly trend detected in {city} — score: {anomaly_score:.2f}"
            )
            db.add(alert)
            db.commit()

    finally:
        db.close()

