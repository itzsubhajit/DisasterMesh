"""
DisasterMesh Backend
Step 35 - Database Table Initialization

Creates the six core DisasterMesh database tables defined in
the project report and SRS:

    users
    nodes
    messages
    routes
    emergency_requests
    logs

This script is intentionally separate from database.py so that
database connection configuration and schema initialization remain
cleanly separated.
"""

import sys
from pathlib import Path

from sqlalchemy import inspect

# ---------------------------------------------------------------------------
# MAKE THE BACKEND PACKAGE IMPORTABLE WHEN THIS FILE IS RUN DIRECTLY
# ---------------------------------------------------------------------------

BACKEND_DIR = Path(__file__).resolve().parent.parent

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(
        0,
        str(BACKEND_DIR)
    )


from app.database import Base, engine
from app import models  # noqa: F401 - registers all ORM models with Base.metadata


# ---------------------------------------------------------------------------
# EXPECTED DISASTERMESH TABLES
# ---------------------------------------------------------------------------

EXPECTED_TABLES = [
    "users",
    "nodes",
    "messages",
    "routes",
    "emergency_requests",
    "logs"
]


# ---------------------------------------------------------------------------
# INITIALIZE DATABASE TABLES
# ---------------------------------------------------------------------------

def initialize_tables() -> None:
    """
    Create all registered SQLAlchemy tables if they do not already exist.
    """

    print(
        "Initializing DisasterMesh database tables..."
    )

    Base.metadata.create_all(
        bind=engine
    )

    inspector = inspect(
        engine
    )

    actual_tables = set(
        inspector.get_table_names()
    )

    missing_tables = [
        table
        for table in EXPECTED_TABLES
        if table not in actual_tables
    ]

    if missing_tables:

        raise RuntimeError(
            "Database initialization failed. "
            f"Missing tables: {', '.join(missing_tables)}"
        )

    print(
        "DisasterMesh database tables initialized successfully."
    )

    print(
        "Tables created/verified:"
    )

    for table in EXPECTED_TABLES:

        print(
            f"  [OK] {table}"
        )


# ---------------------------------------------------------------------------
# DIRECT EXECUTION
# ---------------------------------------------------------------------------

if __name__ == "__main__":

    initialize_tables()
