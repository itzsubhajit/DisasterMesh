
from sqlalchemy import inspect, text

from .database import engine


def migrate():
    inspector = inspect(engine)
    columns = {
        column["name"]
        for column in inspector.get_columns("emergency_requests")
    }

    with engine.begin() as connection:
        if "acknowledged_at" not in columns:
            connection.execute(
                text(
                    "ALTER TABLE emergency_requests "
                    "ADD COLUMN acknowledged_at DATETIME"
                )
            )
            print("Added acknowledged_at column.")

        if "assigned_at" not in columns:
            connection.execute(
                text(
                    "ALTER TABLE emergency_requests "
                    "ADD COLUMN assigned_at DATETIME"
                )
            )
            print("Added assigned_at column.")

        # Backfill missing timestamps for existing incidents.
        connection.execute(
            text("""
                UPDATE emergency_requests
                SET acknowledged_at = CURRENT_TIMESTAMP
                WHERE UPPER(status) IN (
                    'ACKNOWLEDGED', 'ASSIGNED', 'IN_PROGRESS', 'RESOLVED'
                )
                AND acknowledged_at IS NULL
            """)
        )

        connection.execute(
            text("""
                UPDATE emergency_requests
                SET assigned_at = CURRENT_TIMESTAMP
                WHERE UPPER(status) IN (
                    'ASSIGNED', 'IN_PROGRESS', 'RESOLVED'
                )
                AND assigned_at IS NULL
            """)
        )

    print("Emergency timestamp migration completed.")


if __name__ == "__main__":
    migrate()
