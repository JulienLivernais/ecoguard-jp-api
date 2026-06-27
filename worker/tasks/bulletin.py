from worker.celery_app import app
from app.core.database import SessionLocal
from app.models.sensor_reading import SensorReading
from app.models.alert import Alert
from datetime import datetime
from openai import OpenAI
from app.core.config import settings
from weasyprint import HTML
import base64

@app.task
def generate_bulletin(date_start: str, date_end: str):
    db = SessionLocal()
    try:
        start = datetime.fromisoformat(date_start)
        end = datetime.fromisoformat(date_end)

        readings = (
            db.query(SensorReading)
            .filter(SensorReading.timestamp >= start)
            .filter(SensorReading.timestamp <= end)
            .order_by(SensorReading.timestamp.asc())
            .all()
        )

        alerts = (
            db.query(Alert)
            .filter(Alert.timestamp >= start)
            .filter(Alert.timestamp <= end)
            .order_by(Alert.timestamp.asc())
            .all()
        )

        readings_text = "Readings summary:\n"
        for r in readings:
            readings_text += f"- {r.city} | {r.timestamp} | AQI: {r.aqi} | PM2.5: {r.pm25} | Temp: {r.temperature}°C | Humidity: {r.humidity}%\n"

        alerts_text = "Alerts:\n"
        for a in alerts:
            alerts_text += f"- {a.alert_type.value.upper()} | {a.city} | {a.message}\n"

        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[ # type: ignore
                {"role": "system",
                 "content": "You are an air quality expert analyzing environmental data across Japan. "
                            "Analyze the readings and alerts provided, identify patterns, "
                            "and formulate hypotheses about observed anomalies."},
                {"role": "user", "content": f"{readings_text}\n\n{alerts_text}"}
            ]
        )
        bulletin_text = response.choices[0].message.content

        html_content = f"""
        <html>
        <body>
            <h1>EcoGuard Japan — Environmental Bulletin</h1>
            <h2>{date_start} to {date_end}</h2>
            <div>{bulletin_text.replace(chr(10), '<br>')}</div>
        </body>
        </html>
        """

        pdf_bytes = HTML(string=html_content).write_pdf()
        pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")
        return pdf_base64

    finally:
        db.close()