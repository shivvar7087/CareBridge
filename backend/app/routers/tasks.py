from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.time import utc_now
from app.database.connection import get_db
from app.database.models import AuditLog, CaregiverRelationship, JourneyTask, Notification, TaskAssignment, User
from app.schemas.common import TaskCreate, TaskOut, TaskStatusInput, TaskUpdate
from app.services.audit import log_action
from app.services.assignments import set_task_assignment
from app.services.notifications import notify
from app.services.journey_service import mark_overdue
from app.services.permissions import can_access_task, patient_id_for_user, require_patient, visible_tasks_query

router = APIRouter(prefix="/api/tasks", tags=["tasks"])
VALID_STATUSES = {"Pending", "In Progress", "Completed", "Overdue", "Needs Verification", "Scheduled"}


@router.get("", response_model=list[TaskOut])
def list_tasks(status_filter: str | None = Query(default=None, alias="status"), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    from app.services.notifications import create_journey_reminders
    from app.database.models import RequiredReport

    today = date.today()
    query = visible_tasks_query(db, user)
    tasks = query.all()
    if mark_overdue(tasks, today):
        db.commit()
        for task in tasks:
            db.refresh(task)
    patient_id = patient_id_for_user(db, user)
    reports = db.query(RequiredReport).filter_by(patient_id=patient_id).all() if user.role == "patient" else []
    create_journey_reminders(db, user.id, tasks, reports, today)
    db.commit()

    query = visible_tasks_query(db, user)
    if status_filter:
        query = query.filter(JourneyTask.status == status_filter)
    return query.order_by(JourneyTask.due_date.asc().nullslast(), JourneyTask.id.desc()).all()


@router.post("", response_model=TaskOut, status_code=201)
def create_task(data: TaskCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    require_patient(user)
    if data.status not in VALID_STATUSES:
        raise HTTPException(status_code=422, detail="Unknown task status.")
    if data.assigned_to_id and not db.query(CaregiverRelationship).filter_by(patient_id=user.id, caregiver_user_id=data.assigned_to_id, can_view_journey=True).first():
        raise HTTPException(status_code=400, detail="Tasks can only be assigned to a caregiver with active access.")
    values = data.model_dump()
    caregiver_id = values.pop("assigned_to_id")
    task = JourneyTask(patient_id=user.id, **values)
    today = date.today()
    if task.due_date and task.due_date < today and task.status in {"Pending", "In Progress", "Scheduled"}:
        task.status = "Overdue"
    db.add(task)
    db.flush()
    if caregiver_id:
        set_task_assignment(db, task, caregiver_id, user.id)
    log_action(db, user.id, "task.created", "journey_task", task.id)
    if caregiver_id:
        notify(db, caregiver_id, "A task was assigned to you", task.title, "task")
    from app.services.notifications import create_journey_reminders
    from app.database.models import RequiredReport
    reports = db.query(RequiredReport).filter_by(patient_id=user.id).all()
    create_journey_reminders(db, user.id, [task], reports, today)
    db.commit()
    db.refresh(task)
    return task


def _editable_task(db: Session, user: User, task_id: int) -> JourneyTask:
    task = db.get(JourneyTask, task_id)
    if not task or not can_access_task(db, user, task):
        raise HTTPException(status_code=404, detail="Task not found.")
    return task


@router.put("/{task_id}", response_model=TaskOut)
def update_task(task_id: int, data: TaskUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    require_patient(user)
    task = _editable_task(db, user, task_id)
    values = data.model_dump(exclude_unset=True)
    if task.source_instruction and ("title" in values or "description" in values):
        task.needs_clinician_verification = True
    if "status" in values and values["status"] not in VALID_STATUSES:
        raise HTTPException(status_code=422, detail="Unknown task status.")
    if values.get("assigned_to_id") and not db.query(CaregiverRelationship).filter_by(patient_id=task.patient_id, caregiver_user_id=values["assigned_to_id"], can_view_journey=True).first():
        raise HTTPException(status_code=400, detail="Tasks can only be assigned to a caregiver with active access.")
    if "assigned_to_id" in values:
        set_task_assignment(db, task, values.pop("assigned_to_id"), user.id)
    for key, value in values.items():
        setattr(task, key, value)
    today = date.today()
    if task.due_date and task.due_date < today and task.status in {"Pending", "In Progress", "Scheduled"}:
        task.status = "Overdue"
    db.add(task)
    from app.services.notifications import create_journey_reminders
    from app.database.models import RequiredReport
    reports = db.query(RequiredReport).filter_by(patient_id=task.patient_id).all()
    create_journey_reminders(db, user.id, [task], reports, today)
    db.commit()
    db.refresh(task)
    return task


@router.get("/{task_id}/history")
def task_history(task_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    task = _editable_task(db, user, task_id)
    audit = db.query(AuditLog).filter_by(entity_type="journey_task", entity_id=str(task.id)).order_by(AuditLog.created_at.desc()).all()
    assignments = db.query(TaskAssignment).filter_by(task_id=task.id).order_by(TaskAssignment.assigned_at.desc()).all()
    return {"task_id": task.id,
            "events": [{"action": row.action, "actor": db.get(User, row.actor_user_id).full_name if row.actor_user_id and db.get(User, row.actor_user_id) else "System", "at": row.created_at} for row in audit],
            "assignments": [{"caregiver": db.get(User, row.caregiver_user_id).full_name if db.get(User, row.caregiver_user_id) else "Caregiver",
                             "assigned_at": row.assigned_at, "unassigned_at": row.unassigned_at, "active": row.is_active} for row in assignments]}


@router.patch("/{task_id}/status", response_model=TaskOut)
def update_status(task_id: int, data: TaskStatusInput, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    task = _editable_task(db, user, task_id)
    if data.status not in VALID_STATUSES:
        raise HTTPException(status_code=422, detail="Unknown task status.")
    if user.role == "caregiver" and data.status not in {"Pending", "In Progress", "Completed"}:
        raise HTTPException(status_code=403, detail="Caregivers cannot change verification or clinical task states.")
    task.status = data.status
    task.completed_at = utc_now() if data.status == "Completed" else None
    if data.status == "Completed" and user.role == "caregiver":
        notify(db, task.patient_id, "Caregiver completed a task", task.title, "task")
    elif data.status == "Completed" and task.assigned_to_id:
        notify(db, task.assigned_to_id, "Patient updated an assigned task", task.title, "task")
    log_action(db, user.id, "task.status_changed", "journey_task", task.id)
    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    require_patient(user)
    task = _editable_task(db, user, task_id)
    log_action(db, user.id, "task.deleted", "journey_task", task.id)
    db.delete(task)
    db.commit()
