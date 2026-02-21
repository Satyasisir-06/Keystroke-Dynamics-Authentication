"""
KeyAuth - Database Models
SQLAlchemy ORM models for users, keystroke profiles, enrollment samples, and auth logs.
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Integer, Text, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from app.database import Base


def generate_uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    username = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    device_type = Column(String(20), default="web")  # web, mobile, both
    is_enrolled = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    keystroke_profile = relationship("KeystrokeProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    enrollment_samples = relationship("EnrollmentSample", back_populates="user", cascade="all, delete-orphan")
    auth_logs = relationship("AuthLog", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(username='{self.username}', enrolled={self.is_enrolled})>"


class KeystrokeProfile(Base):
    __tablename__ = "keystroke_profiles"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), unique=True, nullable=False)
    feature_vectors = Column(JSON, nullable=True)  # Stored training feature vectors
    model_data = Column(Text, nullable=True)  # Base64-encoded trained model (pickle)
    threshold = Column(Float, default=0.85)
    sample_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="keystroke_profile")

    def __repr__(self):
        return f"<KeystrokeProfile(user_id='{self.user_id}', samples={self.sample_count})>"


class EnrollmentSample(Base):
    __tablename__ = "enrollment_samples"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    raw_keystrokes = Column(JSON, nullable=False)  # Raw key events
    features = Column(JSON, nullable=False)  # Extracted feature vector
    device_type = Column(String(20), default="web")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="enrollment_samples")

    def __repr__(self):
        return f"<EnrollmentSample(user_id='{self.user_id}')>"


class AuthLog(Base):
    __tablename__ = "auth_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    confidence_score = Column(Float, nullable=False)
    result = Column(String(10), nullable=False)  # "accepted" or "rejected"
    device_type = Column(String(20), default="web")
    ip_address = Column(String(45), nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="auth_logs")

    def __repr__(self):
        return f"<AuthLog(user_id='{self.user_id}', result='{self.result}', score={self.confidence_score})>"
