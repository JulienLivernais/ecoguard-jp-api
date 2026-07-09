from datetime import datetime, timezone
from app.models.sensor_reading import SensorReading


def test_get_readings_empty(client):
    response = client.get("/readings")
    assert response.status_code == 200
    assert response.json() == []


def test_get_readings_with_data(client, db_session):
    reading = SensorReading(
        city="Tokyo",
        timestamp=datetime.now(timezone.utc),
        aqi=42,
        pm25=42.0,
        pm10=None,
        no2=None,
        o3=None,
        temperature=20.0,
        humidity=93.0,
    )
    db_session.add(reading)
    db_session.commit()

    response = client.get("/readings")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["city"] == "Tokyo"
    assert response.json()[0]["aqi"] == 42