from datetime import date


def detect_missing_steps(tasks, reports, appointments=None):
    """Return administrative gaps that are explicitly represented in stored records."""
    alerts = []
    for task in tasks:
        if task.status == "Overdue":
            alerts.append({"id": f"task-{task.id}", "title": task.title, "reason": "Administrative step is past its due date.", "kind": "task"})
        elif task.status in {"Pending", "Needs Verification"}:
            alerts.append({"id": f"task-{task.id}", "title": task.title,
                           "reason": "This journey step is still open." if task.status == "Pending" else "This suggested step needs review.", "kind": "task"})
    for report in reports:
        if report.status in {"Missing", "Pending Upload", "Needs Verification"}:
            alerts.append({"id": f"report-{report.id}", "title": report.name,
                           "reason": "Required report is missing or still needs verification.", "kind": "report"})
    if appointments:
        for appointment in appointments:
            linked_reports = [r for r in reports if r.appointment_date == appointment.due_date]
            if linked_reports and any(r.status != "Verified" for r in linked_reports):
                alerts.append({"id": f"appointment-{appointment.id}", "title": appointment.title,
                               "reason": "An upcoming appointment has required documents that are not verified.", "kind": "appointment"})
    return alerts[:6]
