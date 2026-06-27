from celery import Celery
from celery.schedules import crontab
from app.core.config import settings

app = Celery(
    "ecoguard-jp-app",
    broker=settings.REDIS_URL,
    result_backend=settings.REDIS_URL,
    include=[
        "worker.tasks.ingest",
        "worker.tasks.inference",
        "worker.tasks.alert",
        "worker.tasks.bulletin",
    ]
)

app.conf.timezone = "Asia/Tokyo"
app.conf.result_backend = settings.REDIS_URL

app.conf.beat_schedule = {
    "ingest-every-hour": {
        "task": "worker.tasks.ingest.ingest_sensor_data",
        "schedule": crontab(minute=0),
    },
}

