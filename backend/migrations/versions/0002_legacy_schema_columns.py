"""Add columns introduced after the initial CareBridge schema.

Revision ID: 0002_legacy_schema_columns
Revises: 0001_initial
"""
from alembic import op
import sqlalchemy as sa

revision = "0002_legacy_schema_columns"
down_revision = "0001_initial"
branch_labels = None
depends_on = None

ADDITIONS = {
    "patient_profiles": {"created_at": sa.DateTime(), "updated_at": sa.DateTime()},
    "caregiver_relationships": {"updated_at": sa.DateTime()},
    "documents": {"consent_at": sa.DateTime()},
    "extracted_document_data": {"created_at": sa.DateTime(), "updated_at": sa.DateTime()},
    "notifications": {"dedupe_key": sa.String(length=180), "updated_at": sa.DateTime()},
}
TIMESTAMP_COLUMNS = {"created_at", "updated_at"}


def upgrade():
    bind = op.get_bind()
    existing_tables = set(sa.inspect(bind).get_table_names())
    added_dedupe_key = False
    for table, columns in ADDITIONS.items():
        if table not in existing_tables:
            continue
        existing_columns = {column["name"] for column in sa.inspect(bind).get_columns(table)}
        for name, column_type in columns.items():
            if name in existing_columns:
                continue
            op.add_column(table, sa.Column(name, column_type, nullable=True))
            existing_columns.add(name)
            if name in TIMESTAMP_COLUMNS:
                bind.execute(sa.text(f'UPDATE "{table}" SET "{name}" = CURRENT_TIMESTAMP WHERE "{name}" IS NULL'))
            if table == "notifications" and name == "dedupe_key":
                added_dedupe_key = True

    if "notifications" in existing_tables:
        unique_dedupe = any(
            index.get("unique") and index.get("column_names") == ["dedupe_key"]
            for index in sa.inspect(bind).get_indexes("notifications")
        ) or any(
            constraint.get("column_names") == ["dedupe_key"]
            for constraint in sa.inspect(bind).get_unique_constraints("notifications")
        )
        if added_dedupe_key or not unique_dedupe:
            op.create_index("uq_notifications_dedupe_key", "notifications", ["dedupe_key"], unique=True)


def downgrade():
    bind = op.get_bind()
    if "notifications" in sa.inspect(bind).get_table_names():
        indexes = {index["name"] for index in sa.inspect(bind).get_indexes("notifications")}
        if "uq_notifications_dedupe_key" in indexes:
            op.drop_index("uq_notifications_dedupe_key", table_name="notifications")
