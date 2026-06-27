from worker.celery_app import app
import requests
from app.core.config import settings
from app.models.sensor_reading import SensorReading
from app.core.database import SessionLocal
from datetime import datetime, timezone
from worker.tasks.alert import check_alerts
from worker.tasks.inference import run_anomaly_detection


# waqi cities
CITIES = ["Tokyo", "Osaka", "Kyoto", "Nagoya", "Sapporo", "Fukuoka", "Hiroshima", "Sendai"]

# open-meteo cities coordinates
CITY_COORDS = {
    "Tokyo": (35.6762, 139.6503),
    "Osaka": (34.6937, 135.5023),
    "Kyoto": (35.0116, 135.7681),
    "Nagoya": (35.1815, 136.9066),
    "Sapporo": (43.0618, 141.3545),
    "Fukuoka": (33.5904, 130.4017),
    "Hiroshima": (34.3853, 132.4553),
    "Sendai": (38.2682, 140.8694),
}

@app.task
def ingest_sensor_data():
    for city in CITIES:

        # waqi data
        url = f"https://api.waqi.info/feed/{city}/?token={settings.WAQI_KEY}"
        response = requests.get(url)
        data = response.json()
        if data.get("status") != "ok":
            continue

        waqi_data = data["data"]
        aqi = waqi_data.get("aqi")
        iaqi = waqi_data.get("iaqi", {})
        pm25 = iaqi.get("pm25", {}).get("v")
        pm10 = iaqi.get("pm10", {}).get("v")
        no2 = iaqi.get("no2", {}).get("v")
        o3 = iaqi.get("o3", {}).get("v")

        # open-meteo data
        lat, lon = CITY_COORDS[city]
        meteo_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m"
        meteo_response = requests.get(meteo_url)
        meteo_data = meteo_response.json()

        current = meteo_data.get("current", {})
        temperature = current.get("temperature_2m")
        humidity = current.get("relative_humidity_2m")

        db = SessionLocal()
        try:
            reading = SensorReading(
                city=city,
                timestamp=datetime.now(timezone.utc),
                aqi=aqi,
                pm25=pm25,
                pm10=pm10,
                no2=no2,
                o3=o3,
                temperature=temperature,
                humidity=humidity,
            )
            db.add(reading)
            db.commit()
            db.refresh(reading)
            check_alerts.delay(reading.id)
            run_anomaly_detection.delay(city)
        finally:
            db.close()


