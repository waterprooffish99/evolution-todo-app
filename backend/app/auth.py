"""
Authentication and authorization utilities for the Evolution Todo API.

This module handles JWT token verification and The Identity Law enforcement.
All API endpoints must verify JWT tokens to extract the authenticated user_id.
"""

from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import os
from dotenv import load_dotenv

load_dotenv()

# Shared secret with Better Auth (frontend)
BETTER_AUTH_SECRET = os.getenv("BETTER_AUTH_SECRET")

if not BETTER_AUTH_SECRET:
    raise ValueError("BETTER_AUTH_SECRET environment variable is required")

# HTTPBearer security scheme
security = HTTPBearer()


def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> int:
    """
    Verify JWT token and extract authenticated user_id.

    This function is used as a FastAPI dependency to protect endpoints.
    It verifies the JWT signature using the shared BETTER_AUTH_SECRET
    and extracts the user_id claim from the token payload.

    Args:
        credentials: HTTPAuthorizationCredentials from Authorization header

    Returns:
        int: Authenticated user_id extracted from JWT

    Raises:
        HTTPException(401): If token is missing, invalid, or expired

    Usage:
        @app.get("/protected")
        async def protected_route(user_id: int = Depends(verify_token)):
            # user_id is the authenticated user's ID
            pass
    """
    try:
        # Decode and verify JWT
        payload = jwt.decode(
            credentials.credentials,
            BETTER_AUTH_SECRET,
            algorithms=["HS256"]
        )

        # Extract user_id from token
        user_id: int = payload.get("user_id")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user_id claim"
            )

        return user_id

    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )


def check_user_authorization(authenticated_user_id: int, url_user_id: int) -> None:
    """
    Enforce The Identity Law: URL user_id must match authenticated user_id.

    This prevents users from accessing or modifying other users' data by
    ensuring the user_id in the URL path matches the user_id from the JWT token.

    Args:
        authenticated_user_id: User ID extracted from JWT token
        url_user_id: User ID from the URL path parameter

    Raises:
        HTTPException(403): If user_ids don't match (attempting to access another user's data)

    Usage:
        @app.get("/api/{user_id}/tasks")
        async def get_tasks(
            user_id: int,
            authenticated_user_id: int = Depends(verify_token)
        ):
            check_user_authorization(authenticated_user_id, user_id)
            # Proceed with request...
    """
    if authenticated_user_id != url_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Cannot access another user's data"
        )
