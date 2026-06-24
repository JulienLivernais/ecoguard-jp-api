from fastapi import FastAPI
from app.routers import alerts, bulletins, readings

app = FastAPI(
    title="Ecoguard-JP",
    description="Monitor air quality and environmental conditions across Japan in real time",
    version="1.0.0",
)

app.include_router(alerts.router)
app.include_router(bulletins.router)
app.include_router(readings.router)

