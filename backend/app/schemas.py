"""
KeyAuth - Pydantic Schemas
Request/Response models for API validation
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


# ── Keystroke Data ──────────────────────────────────────────────

class KeystrokeEvent(BaseModel):
    """A single key press/release event."""
    key: str = Field(..., description="The key character pressed")
    press_time: float = Field(..., description="Timestamp when key was pressed (ms)")
    release_time: float = Field(..., description="Timestamp when key was released (ms)")
    pressure: Optional[float] = Field(None, description="Touch pressure (mobile only, 0-1)")
    touch_size: Optional[float] = Field(None, description="Touch area size (mobile only)")


class KeystrokeData(BaseModel):
    """Collection of keystroke events from a typing session."""
    keystrokes: List[KeystrokeEvent] = Field(..., min_length=5, description="List of keystroke events")
    device_type: str = Field(default="web", description="Device type: web, mobile")


# ── Registration & Enrollment ───────────────────────────────────

class RegisterRequest(BaseModel):
    """Initial user registration with first typing sample."""
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    name: str = Field(..., min_length=1, max_length=100, description="Full name")
    keystrokes: List[KeystrokeEvent] = Field(..., min_length=5, description="First enrollment typing sample")
    device_type: str = Field(default="web")


class EnrollRequest(BaseModel):
    """Additional enrollment sample submission."""
    username: str = Field(..., description="Username to enroll sample for")
    keystrokes: List[KeystrokeEvent] = Field(..., min_length=5)
    device_type: str = Field(default="web")


class EnrollmentStatusResponse(BaseModel):
    """Enrollment progress for a user."""
    username: str
    name: str
    samples_collected: int
    samples_required: int
    is_enrolled: bool
    message: str


# ── Authentication ──────────────────────────────────────────────

class AuthRequest(BaseModel):
    """Login attempt with keystroke data."""
    username: str = Field(..., description="Username to authenticate")
    keystrokes: List[KeystrokeEvent] = Field(..., min_length=5)
    device_type: str = Field(default="web")


class AuthResponse(BaseModel):
    """Authentication result."""
    authenticated: bool
    confidence_score: float
    message: str
    token: Optional[str] = None


# ── User Profile ────────────────────────────────────────────────

class UserProfile(BaseModel):
    """User profile information."""
    id: str
    username: str
    name: str
    device_type: str
    is_enrolled: bool
    enrollment_samples: int
    security_score: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AuthLogEntry(BaseModel):
    """Single authentication attempt log."""
    id: str
    confidence_score: float
    result: str
    device_type: str
    ip_address: Optional[str]
    timestamp: datetime

    class Config:
        from_attributes = True


class AuthHistoryResponse(BaseModel):
    """Authentication history for a user."""
    username: str
    total_attempts: int
    success_rate: float
    avg_confidence: float
    history: List[AuthLogEntry]


# ── General ─────────────────────────────────────────────────────

class MessageResponse(BaseModel):
    """Generic message response."""
    message: str
    success: bool = True
