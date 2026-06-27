from worker.celery_app import app
from app.core.database import SessionLocal
from app.models.sensor_reading import SensorReading
from app.models.alert import Alert, AlertType, AlertParameter


THRESHOLDS = {
    "aqi": 100,        # AQI > 100 = unhealthy for sensitive groups
    "temperature": 35, # heatwave °C
    "humidity": 80,    # very humid %
}


@app.task
def check_alerts(reading_id: int):
    db = SessionLocal()
    try:
        reading = db.query(SensorReading).filter(SensorReading.id == reading_id).first()
        if not reading:
            return

        alerts_to_save = []

        if reading.aqi and reading.aqi > THRESHOLDS["aqi"]:
            alerts_to_save.append(Alert(
                city=reading.city,
                timestamp=reading.timestamp,
                alert_type=AlertType.spike,
                parameter=AlertParameter.aqi,
                value=reading.aqi,
                threshold=THRESHOLDS["aqi"],
                message=f"AQI spike in {reading.city}: {reading.aqi} exceeds threshold of {THRESHOLDS['aqi']}"
            ))

        if reading.temperature and reading.temperature > THRESHOLDS["temperature"]:
            alerts_to_save.append(Alert(
                city=reading.city,
                timestamp=reading.timestamp,
                alert_type=AlertType.spike,
                parameter=AlertParameter.temperature,
                value=reading.temperature,
                threshold=THRESHOLDS["temperature"],
                message=f"Temperature spike in {reading.city}: {reading.temperature}°C exceeds threshold of {THRESHOLDS['temperature']}°C"
            ))

        if reading.humidity and reading.humidity > THRESHOLDS["humidity"]:
            alerts_to_save.append(Alert(
                city=reading.city,
                timestamp=reading.timestamp,
                alert_type=AlertType.spike,
                parameter=AlertParameter.humidity,
                value=reading.humidity,
                threshold=THRESHOLDS["humidity"],
                message=f"Humidity spike in {reading.city}: {reading.humidity}% exceeds threshold of {THRESHOLDS['humidity']}%"
            ))

        for alert in alerts_to_save:
            db.add(alert)
        db.commit()

    finally:
        db.close()


