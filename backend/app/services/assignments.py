from app.core.time import utc_now
from app.database.models import TaskAssignment


def set_task_assignment(db, task, caregiver_id: int | None, assigned_by_id: int):
    if task.assigned_to_id == caregiver_id:
        return
    active = db.query(TaskAssignment).filter_by(task_id=task.id, is_active=True).all()
    for assignment in active:
        assignment.is_active = False
        assignment.unassigned_at = utc_now()
    task.assigned_to_id = caregiver_id
    if caregiver_id is not None:
        db.add(TaskAssignment(task_id=task.id, caregiver_user_id=caregiver_id, assigned_by_id=assigned_by_id))
