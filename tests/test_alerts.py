from datetime import datetime, timezone
from app.models.alert import Alert, AlertType, AlertParameter


def test_get_alerts_empty(client):
    response = client.get("/alerts")
    assert response.status_code == 200
    assert response.json() == []


def test_get_alerts_with_data(client, db_session):
    reading = Alert(
        city="Tokyo",
        timestamp=datetime.now(timezone.utc),
        alert_type=AlertType.spike,
        parameter=AlertParameter.humidity,
        value=93.0,
        threshold=80.0,
        anomaly_score=None,
        message='Humidity spike in Tokyo'
    )
    db_session.add(reading)
    db_session.commit()

    response = client.get("/alerts")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["city"] == "Tokyo"
    assert response.json()[0]["alert_type"] == "spike"