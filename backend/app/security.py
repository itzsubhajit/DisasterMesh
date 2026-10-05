"""
DisasterMesh Backend
Step 37 - Security Foundation

This module provides the security primitives required by DisasterMesh:

    * bcrypt password hashing and verification
    * JWT access-token creation
    * JWT access-token decoding

The project report specifies JWT authentication and bcrypt password
hashing for the backend security layer.

Authentication routes and role-based authorization will be implemented
in the next backend step.
"""

import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext


# ===========================================================================
# JWT CONFIGURATION
# ===========================================================================

# The production/deployment secret should always be provided through an
# environment variable. The fallback keeps local development simple and
# will be replaced before deployment.
SECRET_KEY = os.getenv(
    "DISASTERMESH_SECRET_KEY",
    "DISASTERMESH_DEVELOPMENT_SECRET_CHANGE_BEFORE_DEPLOYMENT"
)

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 60


# ===========================================================================
# PASSWORD HASHING
# ===========================================================================

password_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def hash_password(password: str) -> str:
    """
    Hash a plaintext password using bcrypt.

    Args:
        password: Plaintext password.

    Returns:
        A bcrypt password hash.
    """

    if not password:
        raise ValueError(
            "Password cannot be empty."
        )

    return password_context.hash(
        password
    )


def verify_password(
    plain_password: str,
    password_hash: str
) -> bool:
    """
    Verify a plaintext password against a stored bcrypt hash.

    Args:
        plain_password: Password supplied during login.
        password_hash: Hash stored in the database.

    Returns:
        True when the password matches; otherwise False.
    """

    if not plain_password or not password_hash:
        return False

    return password_context.verify(
        plain_password,
        password_hash
    )


# ===========================================================================
# JWT TOKEN CREATION
# ===========================================================================

def create_access_token(
    subject: str,
    role: str,
    name: str,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a signed JWT access token.

    The token contains:
        sub  -> username
        role -> ADMIN or OPERATOR
        name -> display name
        exp  -> expiration time
    """

    if not subject:
        raise ValueError(
            "Token subject cannot be empty."
        )

    if not role:
        raise ValueError(
            "Token role cannot be empty."
        )

    if not name:
        raise ValueError(
            "Token name cannot be empty."
        )

    if expires_delta is None:
        expires_delta = timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )

    expires_at = (
        datetime.now(timezone.utc) +
        expires_delta
    )

    payload: Dict[str, Any] = {
        "sub": subject,
        "role": role,
        "name": name,
        "exp": expires_at
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


# ===========================================================================
# JWT TOKEN DECODING
# ===========================================================================

def decode_access_token(
    token: str
) -> Optional[Dict[str, Any]]:
    """
    Decode and validate a DisasterMesh JWT access token.

    Returns:
        Decoded token payload when valid.
        None when the token is invalid or expired.
    """

    if not token:
        return None

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        subject = payload.get(
            "sub"
        )

        role = payload.get(
            "role"
        )

        if not subject or not role:
            return None

        return payload

    except JWTError:
        return None


# ===========================================================================
# SECURITY SELF-TEST
# ===========================================================================

def security_self_test() -> bool:
    """
    Run a small local verification of bcrypt and JWT operations.

    This function does not write to the database and is intended only
    for development verification.
    """

    test_password = (
        "DisasterMesh_Test_Password_123!"
    )

    hashed = hash_password(
        test_password
    )

    if not hashed.startswith(
        "$2"
    ):
        return False

    if not verify_password(
        test_password,
        hashed
    ):
        return False

    if verify_password(
        "WrongPassword",
        hashed
    ):
        return False

    token = create_access_token(
        subject="test_operator",
        role="OPERATOR",
        name="Test Operator"
    )

    payload = decode_access_token(
        token
    )

    if not payload:
        return False

    if payload.get("sub") != "test_operator":
        return False

    if payload.get("role") != "OPERATOR":
        return False

    if payload.get("name") != "Test Operator":
        return False

    return True


# ===========================================================================
# DIRECT EXECUTION
# ===========================================================================

if __name__ == "__main__":

    print(
        "DisasterMesh Security Foundation"
    )

    if security_self_test():

        print(
            "DisasterMesh password hashing OK."
        )

        print(
            "DisasterMesh JWT creation/validation OK."
        )

        print(
            "DisasterMesh security foundation OK."
        )

    else:

        raise RuntimeError(
            "DisasterMesh security self-test failed."
        )
