from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import Task, Activity

router = APIRouter()

@router.post("/")
def create_task(title: str, project_id: int, db: Session = Depends(get_db)):
    task = Task(title=title, project_id=project_id)
    db.add(task)
    db.add(Activity(action=f"Task created: {title}"))
    db.commit()
    return task
