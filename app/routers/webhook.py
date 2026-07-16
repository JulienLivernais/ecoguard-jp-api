from fastapi import APIRouter, Depends
from app.schemas.webhook import WebhookCreate
from app.models.webhook import Webhook
from app.core.database import get_db
from sqlalchemy.orm import Session


router = APIRouter()


@router.post("/webhook")
def create_webhook(webhook: WebhookCreate, db: Session = Depends(get_db)):
    db_webhook = Webhook(url=webhook.url)
    db.add(db_webhook)
    db.commit()
    db.refresh(db_webhook)
    return db_webhook



