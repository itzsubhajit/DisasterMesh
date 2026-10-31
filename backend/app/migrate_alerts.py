
"""
DisasterMesh - Alert Database Migration

Creates the alerts table without modifying existing tables or records.
"""

from sqlalchemy import inspect

from .database import engine, test_database_connection
from .alert_models import Alert


def migrate():
    print("Starting DisasterMesh alert migration...")

    if not test_database_connection():
        raise RuntimeError("Database connection failed.")

    Alert.__table__.create(
        bind=engine,
        checkfirst=True,
    )

    inspector = inspect(engine)

    if "alerts" not in inspector.get_table_names():
        raise RuntimeError("Alerts table was not created.")

    required_columns = {
        "alert_id",
        "fingerprint",
        "alert_type",
        "severity",
        "title",
        "description",
        "source_type",
        "source_id",
        "status",
        "created_at",
        "last_triggered_at",
        "acknowledged_at",
        "resolved_at",
        "occurrence_count",
    }

    actual_columns = {
        column["name"]
        for column in inspector.get_columns("alerts")
    }

    missing = required_columns - actual_columns

    if missing:
        raise RuntimeError(
            f"Missing alert columns: {sorted(missing)}"
        )

    print("Alerts table created or verified successfully.")
    print("Existing database tables were preserved.")


if __name__ == "__main__":
    migrate()
