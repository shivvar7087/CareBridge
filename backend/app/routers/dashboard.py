from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database.connection import get_db
from app.database.models import AuditLog, CaregiverRelationship, JourneyTask, Notification, RequiredReport, User
from app.services.missing_step_service import detect_missing_steps
from app.services.journey_service import mark_overdue
from app.services.notifications import create_journey_reminders
from app.services.permissions import patient_id_for_user, visible_tasks_query

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("")
def dashboard(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    patient_id = patient_id_for_user(db, user)
    tasks = visible_tasks_query(db, user).all()
    today = date.today()
    if mark_overdue(tasks, today):
        db.commit()
    tasks = visible_tasks_query(db, user).all()
    reports = db.query(RequiredReport).filter_by(patient_id=patient_id).all() if user.role == "patient" else []
    appointments = [t for t in tasks if t.category == "Appointment" and t.due_date and t.due_date >= today]
    caregivers = db.query(CaregiverRelationship).filter_by(patient_id=patient_id, can_view_journey=True).count()
    notifications_query = db.query(Notification).filter_by(user_id=user.id)
    recent_notifications = notifications_query.order_by(Notification.created_at.desc()).limit(5).all()
    counts = {s: sum(1 for task in tasks if task.status == s) for s in ["Completed", "Pending", "In Progress", "Overdue", "Needs Verification", "Scheduled"]}
    all_patient_tasks = db.query(JourneyTask).filter_by(patient_id=patient_id).all()
    appointments_all = [t for t in all_patient_tasks if t.category == "Appointment" and t.due_date and t.due_date >= today]
    missing = detect_missing_steps(all_patient_tasks, reports, appointments_all)
    assignments = db.query(JourneyTask).filter(JourneyTask.patient_id == patient_id, JourneyTask.assigned_to_id.is_not(None)).all()
    if user.role == "caregiver":
        assignments = [t for t in assignments if t.assigned_to_id == user.id]
    caregiver_activity = [{"task_id": task.id, "task_title": task.title,
                           "caregiver_name": db.get(User, task.assigned_to_id).full_name if task.assigned_to_id and db.get(User, task.assigned_to_id) else "Caregiver",
                           "status": task.status, "due_date": task.due_date} for task in assignments[:4]]
    create_journey_reminders(db, user.id, tasks, reports, today)
    db.commit()
    return {
        "patient": {"id": patient_id, "name": db.get(User, patient_id).full_name, "is_demo": db.get(User, patient_id).is_demo},
        "summary": {"total_tasks": len(tasks), "completed_tasks": counts["Completed"], "pending_tasks": counts["Pending"] + counts["In Progress"] + counts["Scheduled"],
                    "overdue_tasks": counts["Overdue"], "required_reports": len(reports), "caregiver_count": caregivers},
        "task_status": [{"name": "Completed", "value": counts["Completed"]}, {"name": "In progress", "value": counts["In Progress"] + counts["Pending"]},
                        {"name": "Scheduled", "value": counts["Scheduled"]}, {"name": "Overdue", "value": counts["Overdue"]},
                        {"name": "Needs verification", "value": counts["Needs Verification"]}],
        "journey_progress": {"completed": counts["Completed"], "remaining": max(0, len(tasks) - counts["Completed"])},
        "upcoming_appointments": [{"id": t.id, "title": t.title, "due_date": t.due_date, "description": t.description, "status": t.status} for t in appointments[:3]],
        "reports": [{"id": r.id, "name": r.name, "status": r.status, "appointment_date": r.appointment_date} for r in reports[:4]],
        "caregiver_activity": caregiver_activity,
        "recent_notifications": [{"id": n.id, "title": n.title, "message": n.message, "kind": n.kind,
                                  "is_read": n.is_read, "created_at": n.created_at} for n in recent_notifications],
        "missing_steps": missing,
    }
