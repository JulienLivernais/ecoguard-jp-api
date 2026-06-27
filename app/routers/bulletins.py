from fastapi import APIRouter
from app.schemas.bulletin import BulletinCreate
from worker.tasks.bulletin import generate_bulletin

router = APIRouter()

@router.post("/bulletins")
def create_bulletin(bulletin: BulletinCreate):
    task = generate_bulletin.delay(
        date_start=bulletin.date_start.isoformat(),
        date_end=bulletin.date_end.isoformat()
    )
    return {"task_id": task.id}



