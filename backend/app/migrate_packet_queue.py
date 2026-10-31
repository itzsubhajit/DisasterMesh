
"""
DisasterMesh - Packet Queue Database Migration

Creates the packet_queue table without modifying existing data.
"""

from sqlalchemy import inspect

from .database import Base, engine, test_database_connection
from .queue_models import PacketQueue


def migrate():
    print("Starting Packet Queue database migration...")

    if not test_database_connection():
        raise RuntimeError("Database connection failed.")

    Base.metadata.create_all(
        bind=engine,
        tables=[PacketQueue.__table__],
        checkfirst=True,
    )

    inspector = inspect(engine)

    if "packet_queue" not in inspector.get_table_names():
        raise RuntimeError("Packet queue table was not created.")

    columns = {
        column["name"]
        for column in inspector.get_columns("packet_queue")
    }

    required_columns = {
        "queue_id",
        "message_id",
        "sender_id",
        "receiver_id",
        "category",
        "priority",
        "content",
        "latitude",
        "longitude",
        "ttl",
        "hop_count",
        "status",
        "attempt_count",
        "max_attempts",
        "queued_at",
        "last_attempt_at",
        "next_retry_at",
        "expires_at",
        "synced_at",
        "last_error",
    }

    missing = required_columns - columns

    if missing:
        raise RuntimeError(
            f"Packet queue migration incomplete. Missing: {sorted(missing)}"
        )

    print("Packet queue table created or verified successfully.")
    print("Existing database tables were preserved.")


if __name__ == "__main__":
    migrate()
