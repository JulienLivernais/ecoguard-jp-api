from fastapi import FastAPI
from app.routers import alerts, bulletins, readings
from worker.celery_app import app as celery_app
from celery.result import AsyncResult


app = FastAPI(
    title="Ecoguard-JP",
    description="Monitor air quality and environmental conditions across Japan in real time",
    version="1.0.0",
)


app.include_router(alerts.router)
app.include_router(bulletins.router)
app.include_router(readings.router)


@app.get("/")
def root():
    return {"status": "ok"}


@app.get("/tasks/{task_id}")
def get_task_status(task_id: str):
    task = AsyncResult(task_id, app=celery_app)
    return {
        "task_id": task_id,
        "status": task.status,
        "result": task.result if task.ready() else None
    }

