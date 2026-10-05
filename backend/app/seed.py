"""
DisasterMesh Backend
Step 40 - Initial Database Seed

Creates the initial dashboard users required for development
and authentication testing.
"""

from sqlalchemy.orm import Session

from .database import SessionLocal, initialize_database
from .models import User
from .security import hash_password


INITIAL_USERS = [
    {
        "name": "System Administrator",
        "username": "admin",
        "password": "admin123",
        "role": "ADMIN",
    },
    {
        "name": "Rescue Operator",
        "username": "operator",
        "password": "operator123",
        "role": "OPERATOR",
    },
]


def seed_users(db: Session) -> None:
    """
    Create the initial DisasterMesh dashboard users.

    Existing users are not modified, so this script can safely
    be executed more than once.
    """

    for user_data in INITIAL_USERS:

        existing_user = (
            db.query(User)
            .filter(User.username == user_data["username"])
            .first()
        )

        if existing_user is not None:
            print(
                f"[SKIP] User '{user_data['username']}' "
                f"already exists."
            )
            continue

        user = User(
            name=user_data["name"],
            username=user_data["username"],
            password_hash=hash_password(user_data["password"]),
            role=user_data["role"],
        )

        db.add(user)

        print(
            f"[CREATE] User '{user_data['username']}' "
            f"created successfully."
        )

    db.commit()


def main() -> None:
    """
    Initialize the database and seed the initial users.
    """

    print("DisasterMesh Initial Database Seed")
    print("----------------------------------")

    initialize_database()

    db = SessionLocal()

    try:
        seed_users(db)
        print("----------------------------------")
        print("DisasterMesh initial users seeded successfully.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()