from app.database.models import AuditLog


def log_action(db, actor_id: int | None, action: str, entity_type: str, entity_id: int | str):
    db.add(AuditLog(actor_user_id=actor_id, action=action, entity_type=entity_type, entity_id=str(entity_id)))
