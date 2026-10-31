
"""
DisasterMesh - User Management Database Migration

Adds account activation and JWT version tracking.
Preserves all existing user records.
"""

from sqlalchemy import inspect, text

from .database import engine, test_database_connection


def migrate():
    print("Starting User Management migration...")

    if not test_database_connection():
        raise RuntimeError("Database connection failed.")

    inspector = inspect(engine)

    if "users" not in inspector.get_table_names():
        raise RuntimeError("The users table does not exist.")

    columns = {
        column["name"]
        for column in inspector.get_columns("users")
    }

    with engine.begin() as connection:

        if "is_active" not in columns:
            connection.execute(
                text(
                    "ALTER TABLE users "
                    "ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT 1"
                )
            )
            print("Added is_active column.")

        if "token_version" not in columns:
            connection.execute(
                text(
                    "ALTER TABLE users "
                    "ADD COLUMN token_version INTEGER NOT NULL DEFAULT 0"
                )
            )
            print("Added token_version column.")

    inspector = inspect(engine)

    final_columns = {
        column["name"]
        for column in inspector.get_columns("users")
    }

    required = {"is_active", "token_version"}
    missing = required - final_columns

    if missing:
        raise RuntimeError(
            f"User migration incomplete: {sorted(missing)}"
        )

    print("User Management migration completed successfully.")
    print("Existing user accounts were preserved.")


if __name__ == "__main__":
    migrate()
