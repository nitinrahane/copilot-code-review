"""
Authentication endpoints for the High School Management System API
"""

from fastapi import APIRouter, Header, HTTPException
from typing import Dict, Any, Optional

from ..database import (
    create_session,
    teachers_collection,
    validate_session_token,
    verify_password,
)

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)


@router.post("/login")
def login(username: str, password: str) -> Dict[str, Any]:
    """Login a teacher account"""
    # Find the teacher in the database
    teacher = teachers_collection.find_one({"_id": username})

    # Verify password using Argon2 verifier from database.py
    if not teacher or not verify_password(teacher.get("password", ""), password):
        raise HTTPException(
            status_code=401, detail="Invalid username or password")

    token = create_session(teacher["username"])

    # Return teacher information (excluding password)
    return {
        "username": teacher["username"],
        "display_name": teacher["display_name"],
        "role": teacher["role"],
        "token": token,
    }


@router.get("/check-session")
def check_session(
    username: Optional[str] = None,
    authorization: Optional[str] = Header(default=None),
) -> Dict[str, Any]:
    """Check whether an existing session is valid.

    Supports Bearer token validation and a username fallback for compatibility.
    """
    teacher = None

    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:].strip()
        teacher = validate_session_token(token)
    elif username:
        teacher = teachers_collection.find_one({"_id": username})

    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    return {
        "username": teacher["username"],
        "display_name": teacher["display_name"],
        "role": teacher["role"]
    }
