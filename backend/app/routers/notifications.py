from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database.connection import get_db
from app.database.models import Notification, User
from app.schemas.common import NotificationOut

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.get("", response_model=list[NotificationOut])
def list_notifications(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    from datetime import date
    from app.services.permissions import patient_id_for_user, visible_tasks_query
    from app.services.journey_service import mark_overdue
    from app.services.notifications import create_journey_reminders
    from app.database.models import RequiredReport

    today = date.today()
    tasks = visible_tasks_query(db, user).all()
    if mark_overdue(tasks, today):
        db.commit()
    patient_id = patient_id_for_user(db, user)
    reports = db.query(RequiredReport).filter_by(patient_id=patient_id).all() if user.role == "patient" else []
    create_journey_reminders(db, user.id, tasks, reports, today)
    db.commit()

    items = db.query(Notification).filter_by(user_id=user.id).order_by(Notification.created_at.desc()).all()
    return items


@router.patch("/{notification_id}/read")
def mark_read(notification_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    item = db.query(Notification).filter_by(id=notification_id, user_id=user.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Notification not found.")
    item.is_read = True
    db.commit()
    return {"ok": True}
