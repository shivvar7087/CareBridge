from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database.models import CaregiverRelationship, JourneyTask, User


def patient_id_for_user(db: Session, user: User) -> int:
    if user.role == "patient":
        return user.id
    relationship = db.query(CaregiverRelationship).filter(
        CaregiverRelationship.caregiver_user_id == user.id,
        CaregiverRelationship.can_view_journey.is_(True),
    ).first()
    if not relationship:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No patient journey has been shared with this account.")
    return relationship.patient_id


def require_patient(user: User):
    if user.role != "patient":
        raise HTTPException(status_code=403, detail="Only the patient can make this change.")


def can_access_task(db: Session, user: User, task: JourneyTask) -> bool:
    if user.role == "patient":
        return task.patient_id == user.id
    return task.assigned_to_id == user.id and db.query(CaregiverRelationship).filter_by(
        patient_id=task.patient_id, caregiver_user_id=user.id, can_view_journey=True
    ).first() is not None


def visible_tasks_query(db: Session, user: User):
    if user.role == "patient":
        return db.query(JourneyTask).filter(JourneyTask.patient_id == user.id)
    return db.query(JourneyTask).join(CaregiverRelationship, CaregiverRelationship.patient_id == JourneyTask.patient_id).filter(
        CaregiverRelationship.caregiver_user_id == user.id,
        CaregiverRelationship.can_view_journey.is_(True),
        or_(JourneyTask.assigned_to_id == user.id),
    )
