from app.database.models import Notification


def notify(db, user_id: int, title: str, message: str, kind: str = "info", dedupe_key: str | None = None):
    if dedupe_key and db.query(Notification).filter_by(dedupe_key=dedupe_key).first():
        return
    db.add(Notification(user_id=user_id, title=title, message=message, kind=kind, dedupe_key=dedupe_key))


def create_journey_reminders(db, user_id: int, tasks, reports, today):
    from datetime import timedelta

    for task in tasks:
        if not task.due_date or task.status == "Completed":
            continue
        days_left = (task.due_date - today).days
        key = f"u:{user_id}:task:{task.id}:{task.status}:{task.due_date.isoformat()}"
        if task.status == "Overdue":
            notify(db, user_id, "Administrative task is overdue", task.title, "task", key)
        elif task.category == "Appointment" and 0 <= days_left <= 7:
            notify(db, user_id, "Upcoming appointment", f"{task.title} is due in {days_left} day(s).", "appointment", key)
        elif 0 <= days_left <= 3:
            notify(db, user_id, "Administrative deadline approaching", f"{task.title} is due in {days_left} day(s).", "task", key)
    for report in reports:
        days_to_appointment = (report.appointment_date - today).days if report.appointment_date else None
        if report.status != "Verified" and days_to_appointment is not None and 0 <= days_to_appointment <= 7:
            key = f"u:{user_id}:report:{report.id}:{report.status}:{report.appointment_date.isoformat()}"
            notify(db, user_id, "Required document needs attention", report.name, "document", key)
