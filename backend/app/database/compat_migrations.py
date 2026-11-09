from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine


SQLITE_ADDITIONS = {
    "patient_profiles": {
        "created_at": "DATETIME",
        "updated_at": "DATETIME",
        "blood_group": "VARCHAR(20)",
        "emergency_contact_name": "VARCHAR(160)",
        "emergency_contact_phone": "VARCHAR(40)",
        "settings_json": "TEXT",
    },
    "caregiver_relationships": {"updated_at": "DATETIME"},
    "documents": {"consent_at": "DATETIME"},
    "extracted_document_data": {"created_at": "DATETIME", "updated_at": "DATETIME"},
    "notifications": {"dedupe_key": "VARCHAR(180)", "updated_at": "DATETIME"},
}
TIMESTAMP_COLUMNS = {"created_at", "updated_at"}


def migrate_legacy_sqlite_schema(engine: Engine) -> None:
    """Additive migration for local SQLite databases created by older app versions."""
    if engine.dialect.name != "sqlite":
        return

    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())
    added_dedupe_key = False

    with engine.begin() as connection:
        for table, columns in SQLITE_ADDITIONS.items():
            if table not in existing_tables:
                continue
            existing_columns = {column["name"] for column in inspect(connection).get_columns(table)}
            for name, column_type in columns.items():
                if name in existing_columns:
                    continue
                connection.execute(text(f'ALTER TABLE "{table}" ADD COLUMN "{name}" {column_type}'))
                existing_columns.add(name)
                if name in TIMESTAMP_COLUMNS:
                    connection.execute(text(f'UPDATE "{table}" SET "{name}" = CURRENT_TIMESTAMP WHERE "{name}" IS NULL'))
                if table == "notifications" and name == "dedupe_key":
                    added_dedupe_key = True

        if "notifications" in existing_tables:
            unique_dedupe = any(
                index.get("unique") and index.get("column_names") == ["dedupe_key"]
                for index in inspect(connection).get_indexes("notifications")
            ) or any(
                constraint.get("column_names") == ["dedupe_key"]
                for constraint in inspect(connection).get_unique_constraints("notifications")
            )
            if added_dedupe_key or not unique_dedupe:
                connection.execute(text(
                    'CREATE UNIQUE INDEX IF NOT EXISTS "uq_notifications_dedupe_key" ON "notifications" ("dedupe_key")'
                ))
