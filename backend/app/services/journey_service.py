from datetime import date


def mark_overdue(tasks, today: date | None = None) -> bool:
    today = today or date.today()
    changed = False
    for task in tasks:
        if task.status in {"Pending", "In Progress", "Scheduled"} and task.due_date and task.due_date < today:
            task.status = "Overdue"
            changed = True
    return changed
