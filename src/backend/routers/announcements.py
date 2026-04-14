"""
Announcement endpoints for the High School Management System API
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from fastapi import APIRouter, Body, Depends, Header, HTTPException

from ..database import announcements_collection, validate_session_token

router = APIRouter(
    prefix="/announcements",
    tags=["announcements"],
)


def _parse_iso_date(date_value: Optional[str], field_name: str):
    if date_value in (None, ""):
        return None

    try:
        return datetime.strptime(date_value, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"{field_name} must be in YYYY-MM-DD format",
        )


def _serialize_announcement(announcement: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": announcement["_id"],
        "message": announcement["message"],
        "start_date": announcement.get("start_date"),
        "expiration_date": announcement["expiration_date"],
        "created_by": announcement.get("created_by"),
    }


def _require_signed_in(authorization: Optional[str] = Header(default=None)) -> Dict[str, Any]:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Sign-in is required")

    token = authorization[7:].strip()
    teacher = validate_session_token(token)
    if not teacher:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    return teacher


@router.get("", response_model=List[Dict[str, Any]])
def get_active_announcements() -> List[Dict[str, Any]]:
    """Get currently active announcements for public display."""
    today = datetime.utcnow().date().isoformat()

    query = {
        "expiration_date": {"$gte": today},
        "$or": [
            {"start_date": None},
            {"start_date": {"$exists": False}},
            {"start_date": {"$lte": today}},
        ],
    }

    announcements = announcements_collection.find(query).sort("expiration_date", 1)
    return [_serialize_announcement(announcement) for announcement in announcements]


@router.get("/manage", response_model=List[Dict[str, Any]])
def get_all_announcements(_: Dict[str, Any] = Depends(_require_signed_in)) -> List[Dict[str, Any]]:
    """Get all announcements for signed-in users managing announcements."""
    announcements = announcements_collection.find({}).sort("expiration_date", 1)
    return [_serialize_announcement(announcement) for announcement in announcements]


@router.post("", response_model=Dict[str, Any])
def create_announcement(
    payload: Dict[str, Any] = Body(...),
    teacher: Dict[str, Any] = Depends(_require_signed_in),
) -> Dict[str, Any]:
    """Create a new announcement. Expiration date is required."""
    message = str(payload.get("message", "")).strip()
    if not message:
        raise HTTPException(status_code=400, detail="message is required")

    start_date = _parse_iso_date(payload.get("start_date"), "start_date")
    expiration_date = _parse_iso_date(payload.get("expiration_date"), "expiration_date")

    if not expiration_date:
        raise HTTPException(status_code=400, detail="expiration_date is required")

    if start_date and start_date > expiration_date:
        raise HTTPException(status_code=400, detail="start_date must be before expiration_date")

    announcement_id = f"ann_{uuid4().hex}"
    announcement = {
        "_id": announcement_id,
        "message": message,
        "start_date": start_date.isoformat() if start_date else None,
        "expiration_date": expiration_date.isoformat(),
        "created_by": teacher["username"],
    }

    announcements_collection.insert_one(announcement)
    return _serialize_announcement(announcement)


@router.put("/{announcement_id}", response_model=Dict[str, Any])
def update_announcement(
    announcement_id: str,
    payload: Dict[str, Any] = Body(...),
    _: Dict[str, Any] = Depends(_require_signed_in),
) -> Dict[str, Any]:
    """Update an existing announcement."""
    existing = announcements_collection.find_one({"_id": announcement_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Announcement not found")

    message = str(payload.get("message", "")).strip()
    if not message:
        raise HTTPException(status_code=400, detail="message is required")

    start_date = _parse_iso_date(payload.get("start_date"), "start_date")
    expiration_date = _parse_iso_date(payload.get("expiration_date"), "expiration_date")

    if not expiration_date:
        raise HTTPException(status_code=400, detail="expiration_date is required")

    if start_date and start_date > expiration_date:
        raise HTTPException(status_code=400, detail="start_date must be before expiration_date")

    updated = {
        "message": message,
        "start_date": start_date.isoformat() if start_date else None,
        "expiration_date": expiration_date.isoformat(),
    }

    announcements_collection.update_one(
        {"_id": announcement_id},
        {"$set": updated},
    )

    announcement = announcements_collection.find_one({"_id": announcement_id})
    return _serialize_announcement(announcement)


@router.delete("/{announcement_id}")
def delete_announcement(
    announcement_id: str,
    _: Dict[str, Any] = Depends(_require_signed_in),
) -> Dict[str, str]:
    """Delete an announcement."""
    result = announcements_collection.delete_one({"_id": announcement_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Announcement not found")

    return {"message": "Announcement deleted"}
