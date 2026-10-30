from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database.connection import get_db
from app.database.models import JourneyTask, User
from app.schemas.common import TaskCreate, TaskOut
from app.database.models import CaregiverRelationship
from app.services.audit import log_action
from app.services.notifications import notify
from app.services.assignments import set_task_assignment
from app.services.permissions import patient_id_for_user, require_patient, visible_tasks_query

router = APIRouter(prefix="/api/journey", tags=["journey"])


@router.get("")
def get_journey(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    patient_id = patient_id_for_user(db, user)
    patient = db.get(User, patient_id)
    tasks = visible_tasks_query(db, user).order_by(JourneyTask.due_date.asc().nullslast()).all()
    return {"id": patient_id, "title": f"{patient.full_name}'s healthcare journey", "tasks": tasks}


@router.get("/timeline", response_model=list[TaskOut])
def timeline(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return visible_tasks_query(db, user).order_by(JourneyTask.due_date.asc().nullslast(), JourneyTask.id.asc()).all()


@router.post("", response_model=TaskOut, status_code=201)
def create_journey_task(data: TaskCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    require_patient(user)
    if data.status not in {"Pending", "In Progress", "Completed", "Overdue", "Needs Verification", "Scheduled"}:
        raise HTTPException(status_code=422, detail="Unknown task status.")
    if data.assigned_to_id and not db.query(CaregiverRelationship).filter_by(patient_id=user.id, caregiver_user_id=data.assigned_to_id, can_view_journey=True).first():
        raise HTTPException(status_code=400, detail="Tasks can only be assigned to a caregiver with active access.")
    values = data.model_dump()
    caregiver_id = values.pop("assigned_to_id")
    task = JourneyTask(patient_id=user.id, **values)
    db.add(task)
    db.flush()
    if caregiver_id:
        set_task_assignment(db, task, caregiver_id, user.id)
        notify(db, caregiver_id, "A task was assigned to you", task.title, "task")
    log_action(db, user.id, "task.created", "journey_task", task.id)
    db.commit()
    db.refresh(task)
    return task
