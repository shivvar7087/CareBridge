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
        date_str = task.due_date.isoformat()

        if task.status == "Overdue" or days_left < 0:
            key = f"u:{user_id}:task:{task.id}:overdue:{date_str}"
            overdue_days = abs(days_left)
            day_text = "yesterday" if overdue_days == 1 else f"{overdue_days} days ago"
            notify(
                db,
                user_id,
                "Administrative task is overdue",
                f"'{task.title}' was due on {task.due_date.strftime('%d %b %Y')} ({day_text}). Please review or complete it.",
                "task",
                key,
            )
            # Also notify assigned caregiver if any
            if task.assigned_to_id and task.assigned_to_id != user_id:
                notify(
                    db,
                    task.assigned_to_id,
                    "Assigned task is overdue",
                    f"'{task.title}' assigned to you was due on {task.due_date.strftime('%d %b %Y')} and is now overdue.",
                    "task",
                    f"u:{task.assigned_to_id}:task:{task.id}:overdue:{date_str}",
                )
        elif days_left == 0:
            # Reached current date!
            key = f"u:{user_id}:task:{task.id}:due_today:{date_str}"
            if task.category == "Appointment":
                notify(
                    db,
                    user_id,
                    "Appointment scheduled for TODAY",
                    f"'{task.title}' is scheduled for today. Confirm your clinic time and directions.",
                    "appointment",
                    key,
                )
            else:
                notify(
                    db,
                    user_id,
                    "Task is due TODAY",
                    f"'{task.title}' is scheduled for today. Please review and complete it.",
                    "task",
                    key,
                )
            # Notify caregiver if assigned
            if task.assigned_to_id and task.assigned_to_id != user_id:
                notify(
                    db,
                    task.assigned_to_id,
                    "Assigned task is due TODAY",
                    f"'{task.title}' assigned to you is due today.",
                    "task",
                    f"u:{task.assigned_to_id}:task:{task.id}:due_today:{date_str}",
                )
        elif task.category == "Appointment" and 1 <= days_left <= 7:
            key = f"u:{user_id}:task:{task.id}:upcoming:{date_str}:{days_left}"
            day_text = "tomorrow" if days_left == 1 else f"in {days_left} days"
            notify(
                db,
                user_id,
                "Upcoming appointment",
                f"'{task.title}' is scheduled for {day_text} ({task.due_date.strftime('%d %b %Y')}).",
                "appointment",
                key,
            )
        elif 1 <= days_left <= 3:
            key = f"u:{user_id}:task:{task.id}:due_soon:{date_str}:{days_left}"
            day_text = "tomorrow" if days_left == 1 else f"in {days_left} days"
            notify(
                db,
                user_id,
                "Administrative deadline approaching",
                f"'{task.title}' is due {day_text}.",
                "task",
                key,
            )

    for report in reports:
        days_to_appointment = (report.appointment_date - today).days if report.appointment_date else None
        if report.status != "Verified" and days_to_appointment is not None:
            if days_to_appointment == 0:
                key = f"u:{user_id}:report:{report.id}:today:{report.appointment_date.isoformat()}"
                notify(
                    db,
                    user_id,
                    "Required document needed TODAY",
                    f"'{report.name}' is needed for today's appointment.",
                    "document",
                    key,
                )
            elif 1 <= days_to_appointment <= 7:
                key = f"u:{user_id}:report:{report.id}:{report.status}:{report.appointment_date.isoformat()}"
                notify(
                    db,
                    user_id,
                    "Required document needs attention",
                    f"'{report.name}' is needed for appointment in {days_to_appointment} day(s).",
                    "document",
                    key,
                )
