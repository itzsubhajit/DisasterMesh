"""
DisasterMesh Backend
Step 33 - Database Configuration

This module creates the SQLAlchemy database engine and session
configuration for the DisasterMesh prototype.

Database:
    SQLite

Database file:
    backend/disastermesh.db
"""

from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


# ---------------------------------------------------------------------------
# PROJECT PATHS
# ---------------------------------------------------------------------------

# backend/
# └── app/
#     └── database.py
#
# The parent of "app" is the backend directory.
BACKEND_DIR = Path(__file__).resolve().parent.parent

DATABASE_PATH = BACKEND_DIR / "disastermesh.db"

DATABASE_URL = f"sqlite:///{DATABASE_PATH}"


# ---------------------------------------------------------------------------
# SQLALCHEMY ENGINE
# ---------------------------------------------------------------------------

# SQLite needs check_same_thread=False because FastAPI can handle requests
# across different worker threads during normal development.
engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False
    },
    future=True
)


# ---------------------------------------------------------------------------
# SESSION FACTORY
# ---------------------------------------------------------------------------

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    class_=Session
)


# ---------------------------------------------------------------------------
# BASE CLASS
# ---------------------------------------------------------------------------

class Base(DeclarativeBase):
    """
    Base class for all DisasterMesh SQLAlchemy models.

    The actual database entities will be created in models.py
    during the next backend step.
    """

    pass


# ---------------------------------------------------------------------------
# DATABASE SESSION DEPENDENCY
# ---------------------------------------------------------------------------

def get_db() -> Generator[Session, None, None]:
    """
    Provide a database session to a FastAPI route.

    The session is always closed after the request finishes.
    """

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# ---------------------------------------------------------------------------
# DATABASE CONNECTION TEST
# ---------------------------------------------------------------------------

def test_database_connection() -> bool:
    """
    Test whether the SQLite database can be opened successfully.

    Returns:
        True  -> connection successful
        False -> connection failed
    """

    try:
        with engine.connect() as connection:
            connection.execute(
                text("SELECT 1")
            )

        return True

    except Exception as exc:
        print(
            f"DisasterMesh database connection failed: {exc}"
        )

        return False


# ---------------------------------------------------------------------------
# INITIAL DATABASE SETUP
# ---------------------------------------------------------------------------

def initialize_database() -> None:
    """
    Prepare the SQLite database.

    At Step 33 we intentionally do not create tables yet because the
    SQLAlchemy models are implemented in the next step.

    This function only verifies that the SQLite database is reachable.
    """

    DATABASE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    if test_database_connection():

        print(
            "DisasterMesh SQLite database connection successful."
        )

    else:

        raise RuntimeError(
            "Unable to initialize the DisasterMesh SQLite database."
        )


# ---------------------------------------------------------------------------
# DIRECT EXECUTION
# ---------------------------------------------------------------------------

if __name__ == "__main__":

    print(
        "DisasterMesh Database Configuration"
    )

    print(
        f"Database file: {DATABASE_PATH}"
    )

    print(
        f"Database URL: {DATABASE_URL}"
    )

    initialize_database()
