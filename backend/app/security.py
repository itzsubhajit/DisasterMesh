
"""
DisasterMesh Security Module

Provides bcrypt password hashing and JWT authentication.
"""

import os

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext


# =========================================================
# JWT CONFIGURATION
# =========================================================

SECRET_KEY = os.getenv(
    "DISASTERMESH_SECRET_KEY",
    "DISASTERMESH_DEVELOPMENT_SECRET_CHANGE_BEFORE_DEPLOYMENT",
)

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 60


# =========================================================
# PASSWORD HASHING
# =========================================================

password_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


def hash_password(password: str) -> str:
    if not password:
        raise ValueError("Password cannot be empty.")

    if len(password.encode("utf-8")) > 72:
        raise ValueError("Password cannot exceed 72 UTF-8 bytes.")

    return password_context.hash(password)


def verify_password(
    plain_password: str,
    password_hash: str,
) -> bool:
    if not plain_password or not password_hash:
        return False

    try:
        return password_context.verify(
            plain_password,
            password_hash,
        )
    except (ValueError, TypeError):
        return False


# =========================================================
# JWT TOKEN CREATION
# =========================================================

def create_access_token(
    subject: str,
    role: str,
    name: str,
    expires_delta: Optional[timedelta] = None,
    token_version: int = 0,
) -> str:

    if not subject:
        raise ValueError("Token subject cannot be empty.")

    if not role:
        raise ValueError("Token role cannot be empty.")

    if not name:
        raise ValueError("Token name cannot be empty.")

    if token_version < 0:
        raise ValueError("Token version cannot be negative.")

    if expires_delta is None:
        expires_delta = timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )

    expires_at = (
        datetime.now(timezone.utc) + expires_delta
    )

    payload: Dict[str, Any] = {
        "sub": subject,
        "role": role,
        "name": name,
        "ver": token_version,
        "exp": expires_at,
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


# =========================================================
# JWT TOKEN DECODING
# =========================================================

def decode_access_token(
    token: str,
) -> Optional[Dict[str, Any]]:

    if not token:
        return None

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        subject = payload.get("sub")
        role = payload.get("role")

        if not subject or not role:
            return None

        return payload

    except JWTError:
        return None


# =========================================================
# SECURITY SELF-TEST
# =========================================================

def security_self_test() -> bool:

    test_password = "DisasterMesh_Test_Password_123!"

    hashed = hash_password(test_password)

    if not hashed.startswith("$2"):
        return False

    if not verify_password(test_password, hashed):
        return False

    if verify_password("WrongPassword", hashed):
        return False

    token = create_access_token(
        subject="test_operator",
        role="OPERATOR",
        name="Test Operator",
        token_version=2,
    )

    payload = decode_access_token(token)

    if not payload:
        return False

    if payload.get("sub") != "test_operator":
        return False

    if payload.get("role") != "OPERATOR":
        return False

    if payload.get("ver") != 2:
        return False

    return True


if __name__ == "__main__":

    print("DisasterMesh Security Foundation")

    if security_self_test():
        print("DisasterMesh password hashing OK.")
        print("DisasterMesh JWT creation/validation OK.")
        print("DisasterMesh token version validation OK.")
        print("DisasterMesh security foundation OK.")
    else:
        raise RuntimeError(
            "DisasterMesh security self-test failed."
        )
