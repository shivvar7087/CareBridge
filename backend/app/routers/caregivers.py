import secrets

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database.connection import get_db
from app.database.models import CaregiverRelationship, JourneyTask, Notification, TaskAssignment, User
from app.schemas.common import CaregiverInvite, TaskAssignment
from app.services.audit import log_action
from app.services.assignments import set_task_assignment
from app.services.notifications import notify
from app.services.permissions import require_patient

router = APIRouter(prefix="/api/caregivers", tags=["caregivers"])


@router.get("")
def list_caregivers(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if user.role == "patient":
        rows = db.query(CaregiverRelationship).filter_by(patient_id=user.id).all()
    else:
        rows = db.query(CaregiverRelationship).filter_by(caregiver_user_id=user.id).all()
    return [{"id": row.id, "email": row.invited_email, "name": db.get(User, row.caregiver_user_id).full_name if row.caregiver_user_id and db.get(User, row.caregiver_user_id) else None,
             "patient_name": db.get(User, row.patient_id).full_name if user.role == "caregiver" and db.get(User, row.patient_id) else None,
             "caregiver_user_id": row.caregiver_user_id, "active": row.can_view_journey, "invitation_code": row.invitation_code if not row.caregiver_user_id and user.role == "patient" else None}
            for row in rows]


@router.post("/invite", status_code=201)
def invite(data: CaregiverInvite, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    require_patient(user)
    email = data.email.lower()
    existing = db.query(CaregiverRelationship).filter_by(patient_id=user.id, invited_email=email).first()
    if existing:
        if existing.can_view_journey:
            raise HTTPException(status_code=409, detail="This caregiver already has access or an active invitation.")
        existing.can_view_journey = True
        existing.invitation_code = secrets.token_urlsafe(24)
        relationship = existing
    else:
        relationship = CaregiverRelationship(patient_id=user.id, invited_email=email, invitation_code=secrets.token_urlsafe(24))
        db.add(relationship)
    caregiver = db.query(User).filter_by(email=email, role="caregiver").first()
    if caregiver:
        relationship.caregiver_user_id = caregiver.id
        notify(db, caregiver.id, "A patient shared a healthcare journey", f"{user.full_name} shared their journey with you.", "share")
    db.flush()
    log_action(db, user.id, "caregiver.invited", "caregiver_relationship", relationship.id)
    db.commit()
    return {"id": relationship.id, "email": email, "invitation_code": relationship.invitation_code,
            "registered": caregiver is not None, "instructions": "Share this code with the caregiver. They must register with the invited email and this code." if not caregiver else "Caregiver access is active."}


@router.post("/assign-task")
def assign_task(data: TaskAssignment, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    require_patient(user)
    task_id, caregiver_id = data.task_id, data.caregiver_id
    task = db.query(JourneyTask).filter_by(id=task_id, patient_id=user.id).first()
    relation = db.query(CaregiverRelationship).filter_by(patient_id=user.id, caregiver_user_id=caregiver_id, can_view_journey=True).first()
    if not task or not relation:
        raise HTTPException(status_code=404, detail="Task or shared caregiver not found.")
    set_task_assignment(db, task, caregiver_id, user.id)
    if task.source_instruction:
        task.needs_clinician_verification = True
    notify(db, caregiver_id, "A task was assigned to you", task.title, "task")
    log_action(db, user.id, "task.assigned", "journey_task", task.id)
    db.commit()
    return {"ok": True}


@router.delete("/{relationship_id}", status_code=204)
def remove_caregiver(relationship_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    require_patient(user)
    relationship = db.query(CaregiverRelationship).filter_by(id=relationship_id, patient_id=user.id).first()
    if not relationship:
        raise HTTPException(status_code=404, detail="Caregiver relationship not found.")
    caregiver_id = relationship.caregiver_user_id
    relationship.can_view_journey = False
    if caregiver_id:
        for task in db.query(JourneyTask).filter_by(patient_id=user.id, assigned_to_id=caregiver_id).all():
            set_task_assignment(db, task, None, user.id)
    log_action(db, user.id, "caregiver.access_removed", "caregiver_relationship", relationship.id)
    db.commit()
