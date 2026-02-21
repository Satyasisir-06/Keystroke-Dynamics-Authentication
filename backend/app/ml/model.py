"""
KeyAuth - ML Authentication Model
Trains per-user models and authenticates based on keystroke patterns.

Strategy:
  1. When fewer than ENROLLMENT_SAMPLES_REQUIRED samples:
     → Uses statistical distance matching (Manhattan + cosine similarity)
  2. When enough samples are collected:
     → Trains a Random Forest classifier or One-Class SVM
  3. Returns confidence score 0.0 to 1.0
"""
import base64
import pickle
import numpy as np
from typing import List, Optional, Tuple
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from app.ml.utils import manhattan_distance, cosine_similarity, normalize_features
from app.config import settings


class KeystrokeAuthModel:
    """
    Per-user keystroke authentication model.
    
    Supports two modes:
      - Statistical mode (few samples): uses distance-based matching
      - ML mode (enough samples): uses Isolation Forest for anomaly detection
    """

    def __init__(self):
        self.scaler = StandardScaler()
        self.model = None
        self.training_vectors: List[List[float]] = []
        self.is_trained = False

    def add_training_sample(self, feature_vector: List[float]):
        """Add a feature vector from an enrollment sample."""
        self.training_vectors.append(feature_vector)

    def train(self) -> bool:
        """
        Train the model on collected enrollment samples.
        
        Returns True if training succeeded, False otherwise.
        """
        n_samples = len(self.training_vectors)
        if n_samples < 2:
            return False

        X = np.array(self.training_vectors, dtype=np.float64)

        # Fit scaler
        self.scaler.fit(X)
        X_scaled = self.scaler.transform(X)

        if n_samples >= settings.ENROLLMENT_SAMPLES_REQUIRED:
            # Use Isolation Forest for anomaly detection
            # Contamination set low since all training data is "genuine"
            self.model = IsolationForest(
                n_estimators=100,
                contamination=0.1,
                random_state=42,
            )
            self.model.fit(X_scaled)
            self.is_trained = True
        else:
            # Not enough samples for ML — use statistical mode
            self.is_trained = False

        return True

    def authenticate(self, feature_vector: List[float]) -> Tuple[float, str]:
        """
        Authenticate a typing sample against the user's profile.
        
        Args:
            feature_vector: Feature vector from the authentication attempt
        
        Returns:
            (confidence_score, method): score 0-1, and which method was used
        """
        if not self.training_vectors:
            return 0.0, "no_profile"

        if self.is_trained and self.model is not None:
            return self._ml_authenticate(feature_vector), "isolation_forest"
        else:
            return self._statistical_authenticate(feature_vector), "statistical"

    def _ml_authenticate(self, feature_vector: List[float]) -> float:
        """
        ML-based authentication using Isolation Forest.
        
        The anomaly score is converted to a 0-1 confidence score.
        """
        X = np.array([feature_vector], dtype=np.float64)
        X_scaled = self.scaler.transform(X)

        # score_samples returns anomaly score (higher = more normal)
        raw_score = self.model.score_samples(X_scaled)[0]

        # Convert to 0-1 range using sigmoid-like mapping
        # Isolation Forest scores typically range from -0.5 to 0.5
        # Map so that ~0 raw score → 0.85 confidence (threshold zone)
        confidence = 1.0 / (1.0 + np.exp(-10 * (raw_score + 0.1)))
        return float(np.clip(confidence, 0.0, 1.0))

    def _statistical_authenticate(self, feature_vector: List[float]) -> float:
        """
        Statistical distance-based authentication.
        
        Computes average distance to all training vectors and converts
        to a confidence score. Uses a blend of Manhattan distance and
        cosine similarity.
        """
        if not self.training_vectors:
            return 0.0

        # Normalize all vectors
        test_norm = normalize_features(feature_vector)

        distances = []
        similarities = []
        for train_vec in self.training_vectors:
            train_norm = normalize_features(train_vec)
            dist = manhattan_distance(test_norm, train_norm)
            sim = cosine_similarity(test_norm, train_norm)
            distances.append(dist)
            similarities.append(sim)

        avg_distance = np.mean(distances)
        avg_similarity = np.mean(similarities)

        # Convert distance to confidence (lower distance = higher confidence)
        # Typical normalized Manhattan distances range from 0 to ~len(vector)
        n_features = len(feature_vector)
        distance_confidence = max(0.0, 1.0 - (avg_distance / (n_features * 1.5)))

        # Blend distance confidence with cosine similarity
        # 60% distance, 40% cosine similarity
        confidence = 0.6 * distance_confidence + 0.4 * max(0.0, avg_similarity)

        return float(np.clip(confidence, 0.0, 1.0))

    def serialize(self) -> str:
        """Serialize the model to a base64-encoded string for storage."""
        data = {
            "training_vectors": self.training_vectors,
            "is_trained": self.is_trained,
            "scaler": self.scaler if self.is_trained else None,
            "model": self.model if self.is_trained else None,
        }
        return base64.b64encode(pickle.dumps(data)).decode("utf-8")

    @classmethod
    def deserialize(cls, data_str: str) -> "KeystrokeAuthModel":
        """Deserialize a model from a base64-encoded string."""
        data = pickle.loads(base64.b64decode(data_str.encode("utf-8")))
        instance = cls()
        instance.training_vectors = data.get("training_vectors", [])
        instance.is_trained = data.get("is_trained", False)
        if data.get("scaler") is not None:
            instance.scaler = data["scaler"]
        if data.get("model") is not None:
            instance.model = data["model"]
        return instance
