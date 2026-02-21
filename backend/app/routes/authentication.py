"""
KeyAuth - Authentication Routes
Handles login via keystroke matching.
"""
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, AuthLog
from app.schemas import AuthRequest, AuthResponse
from app.ml.feature_extractor import extract_features
from app.ml.model import KeystrokeAuthModel
from app.auth import create_access_token
from app.security import anti_replay, rate_limiter
from app.config import settings

router = APIRouter(prefix="/api", tags=["Authentication"])


@router.post("/authenticate", response_model=AuthResponse)
def authenticate_user(req: AuthRequest, request: Request, db: Session = Depends(get_db)):
    """
    Authenticate a user by analyzing their keystroke patterns.
    
    Process:
      1. Verify user exists and is enrolled
      2. Check rate limits and anti-replay
      3. Extract features from submitted keystrokes
      4. Load user's trained model
      5. Compare patterns and compute confidence score
      6. If score > threshold → issue JWT token
    """
    # ── Rate Limiting ───────────────────────────────────────────
    if not rate_limiter.is_allowed(req.username):
        remaining = rate_limiter.remaining_attempts(req.username)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many authentication attempts. Please wait before trying again. Remaining: {remaining}",
        )
    rate_limiter.record_attempt(req.username)

    # ── Find User ───────────────────────────────────────────────
    user = db.query(User).filter(User.username == req.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User '{req.username}' not found",
        )

    if not user.is_enrolled:
        profile = user.keystroke_profile
        samples = profile.sample_count if profile else 0
        remaining = settings.ENROLLMENT_SAMPLES_REQUIRED - samples
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User not fully enrolled. {remaining} more typing sample(s) needed.",
        )

    # ── Anti-Replay Check ───────────────────────────────────────
    if not anti_replay.check_and_record(req.keystrokes):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Duplicate submission detected. Please type the phrase again.",
        )

    # ── Extract Features ────────────────────────────────────────
    try:
        features = extract_features(req.keystrokes)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # ── Load Model & Authenticate ───────────────────────────────
    profile = user.keystroke_profile
    if not profile or not profile.model_data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No trained model found for this user.",
        )

    auth_model = KeystrokeAuthModel.deserialize(profile.model_data)
    confidence_score, method = auth_model.authenticate(features["vector"])
    confidence_score = round(confidence_score, 4)

    # ── Decision ────────────────────────────────────────────────
    threshold = profile.threshold or settings.AUTH_CONFIDENCE_THRESHOLD
    authenticated = confidence_score >= threshold

    # Get client IP
    client_ip = request.client.host if request.client else None

    # Log the attempt
    auth_log = AuthLog(
        user_id=user.id,
        confidence_score=confidence_score,
        result="accepted" if authenticated else "rejected",
        device_type=req.device_type,
        ip_address=client_ip,
    )
    db.add(auth_log)
    db.commit()

    # ── Response ────────────────────────────────────────────────
    if authenticated:
        token = create_access_token(data={"sub": user.username, "user_id": user.id})
        return AuthResponse(
            authenticated=True,
            confidence_score=confidence_score,
            message=f"✅ Identity verified (confidence: {confidence_score:.1%}, method: {method})",
            token=token,
        )
    else:
        return AuthResponse(
            authenticated=False,
            confidence_score=confidence_score,
            message=f"❌ Authentication failed. Confidence {confidence_score:.1%} is below threshold {threshold:.1%}.",
            token=None,
        )
