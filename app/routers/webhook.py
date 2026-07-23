from fastapi import APIRouter, Depends, HTTPException
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

@router.delete("/webhook/{webhook_id}")
def delete_webhook(webhook_id: int, db: Session = Depends(get_db)):
    webhook = db.query(Webhook).filter(Webhook.id == webhook_id).first()
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    db.delete(webhook)
    db.commit()
    return {"message": "Webhook deleted"}



