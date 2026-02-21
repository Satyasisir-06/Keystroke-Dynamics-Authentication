"""
KeyAuth - User Profile Routes
Protected endpoints for user data and auth history.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, AuthLog
from app.schemas import UserProfile, AuthHistoryResponse, AuthLogEntry
from app.auth import get_current_user

router = APIRouter(prefix="/api/user", tags=["User Profile"])


@router.get("/profile", response_model=UserProfile)
def get_profile(current_user: User = Depends(get_current_user)):
    """
    Get the authenticated user's profile.
    Requires valid JWT token.
    """
    profile = current_user.keystroke_profile
    samples = profile.sample_count if profile else 0

    # Compute security score based on enrollment completeness and auth history
    security_score = None
    if current_user.is_enrolled and current_user.auth_logs:
        recent_logs = sorted(current_user.auth_logs, key=lambda x: x.timestamp, reverse=True)[:20]
        accepted = sum(1 for log in recent_logs if log.result == "accepted")
        security_score = round((accepted / len(recent_logs)) * 100, 1) if recent_logs else None

    return UserProfile(
        id=current_user.id,
        username=current_user.username,
        name=current_user.name,
        device_type=current_user.device_type,
        is_enrolled=current_user.is_enrolled,
        enrollment_samples=samples,
        security_score=security_score,
        created_at=current_user.created_at,
    )


@router.get("/auth-history", response_model=AuthHistoryResponse)
def get_auth_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get the authenticated user's authentication attempt history.
    Requires valid JWT token.
    """
    logs = (
        db.query(AuthLog)
        .filter(AuthLog.user_id == current_user.id)
        .order_by(AuthLog.timestamp.desc())
        .limit(50)
        .all()
    )

    total = len(logs)
    accepted = sum(1 for log in logs if log.result == "accepted")
    success_rate = round((accepted / total) * 100, 1) if total > 0 else 0.0
    avg_confidence = round(
        sum(log.confidence_score for log in logs) / total * 100, 1
    ) if total > 0 else 0.0

    history = [
        AuthLogEntry(
            id=log.id,
            confidence_score=round(log.confidence_score * 100, 1),
            result=log.result,
            device_type=log.device_type,
            ip_address=log.ip_address,
            timestamp=log.timestamp,
        )
        for log in logs
    ]

    return AuthHistoryResponse(
        username=current_user.username,
        total_attempts=total,
        success_rate=success_rate,
        avg_confidence=avg_confidence,
        history=history,
    )
