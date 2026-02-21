"""
KeyAuth - Registration & Enrollment Routes
Handles user creation and keystroke enrollment sample collection.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, KeystrokeProfile, EnrollmentSample
from app.schemas import (
    RegisterRequest,
    EnrollRequest,
    EnrollmentStatusResponse,
    MessageResponse,
)
from app.ml.feature_extractor import extract_features
from app.ml.model import KeystrokeAuthModel
from app.config import settings

router = APIRouter(prefix="/api", tags=["Registration & Enrollment"])


@router.post("/register", response_model=EnrollmentStatusResponse, status_code=201)
def register_user(req: RegisterRequest, db: Session = Depends(get_db)):
    """
    Register a new user and submit the first enrollment typing sample.
    
    The user must complete additional enrollment samples before they can authenticate.
    """
    # Check if username already exists
    existing = db.query(User).filter(User.username == req.username).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Username '{req.username}' is already taken",
        )

    # Extract features from the first typing sample
    try:
        features = extract_features(req.keystrokes)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Create user
    user = User(
        username=req.username,
        name=req.name,
        device_type=req.device_type,
    )
    db.add(user)
    db.flush()  # Get the user ID

    # Create keystroke profile
    profile = KeystrokeProfile(
        user_id=user.id,
        feature_vectors=[features["vector"]],
        sample_count=1,
    )
    db.add(profile)

    # Store the enrollment sample
    sample = EnrollmentSample(
        user_id=user.id,
        raw_keystrokes=[ks.model_dump() for ks in req.keystrokes],
        features=features["vector"],
        device_type=req.device_type,
    )
    db.add(sample)
    db.commit()

    return EnrollmentStatusResponse(
        username=user.username,
        name=user.name,
        samples_collected=1,
        samples_required=settings.ENROLLMENT_SAMPLES_REQUIRED,
        is_enrolled=False,
        message=f"Registration successful! Please provide {settings.ENROLLMENT_SAMPLES_REQUIRED - 1} more typing samples to complete enrollment.",
    )


@router.post("/enroll", response_model=EnrollmentStatusResponse)
def enroll_sample(req: EnrollRequest, db: Session = Depends(get_db)):
    """
    Submit an additional enrollment typing sample.
    
    After collecting enough samples, the ML model is automatically trained.
    """
    # Find user
    user = db.query(User).filter(User.username == req.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User '{req.username}' not found. Please register first.",
        )

    if user.is_enrolled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already fully enrolled. Use re-enroll to update your typing pattern.",
        )

    # Extract features
    try:
        features = extract_features(req.keystrokes)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Store enrollment sample
    sample = EnrollmentSample(
        user_id=user.id,
        raw_keystrokes=[ks.model_dump() for ks in req.keystrokes],
        features=features["vector"],
        device_type=req.device_type,
    )
    db.add(sample)

    # Update profile
    profile = user.keystroke_profile
    if profile.feature_vectors is None:
        profile.feature_vectors = []

    # SQLAlchemy JSON mutation detection
    vectors = list(profile.feature_vectors)
    vectors.append(features["vector"])
    profile.feature_vectors = vectors
    profile.sample_count = len(vectors)

    # Check if we have enough samples to train the model
    samples_collected = profile.sample_count
    is_enrolled = samples_collected >= settings.ENROLLMENT_SAMPLES_REQUIRED

    if is_enrolled:
        # Train the ML model
        auth_model = KeystrokeAuthModel()
        for vec in profile.feature_vectors:
            auth_model.add_training_sample(vec)
        auth_model.train()

        # Serialize and store the trained model
        profile.model_data = auth_model.serialize()
        user.is_enrolled = True
        message = "🎉 Enrollment complete! Your typing pattern has been learned. You can now authenticate."
    else:
        remaining = settings.ENROLLMENT_SAMPLES_REQUIRED - samples_collected
        message = f"Sample recorded. {remaining} more sample(s) needed to complete enrollment."

    db.commit()

    return EnrollmentStatusResponse(
        username=user.username,
        name=user.name,
        samples_collected=samples_collected,
        samples_required=settings.ENROLLMENT_SAMPLES_REQUIRED,
        is_enrolled=is_enrolled,
        message=message,
    )


@router.get("/enrollment-status/{username}", response_model=EnrollmentStatusResponse)
def get_enrollment_status(username: str, db: Session = Depends(get_db)):
    """Check enrollment progress for a user."""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User '{username}' not found",
        )

    profile = user.keystroke_profile
    samples = profile.sample_count if profile else 0

    return EnrollmentStatusResponse(
        username=user.username,
        name=user.name,
        samples_collected=samples,
        samples_required=settings.ENROLLMENT_SAMPLES_REQUIRED,
        is_enrolled=user.is_enrolled,
        message="Enrollment complete" if user.is_enrolled else f"{settings.ENROLLMENT_SAMPLES_REQUIRED - samples} more sample(s) needed",
    )
