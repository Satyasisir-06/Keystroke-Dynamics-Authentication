"""
KeyAuth - ML Utilities
Data preprocessing and helper functions
"""
import numpy as np
from typing import List, Dict


def normalize_features(features: List[float]) -> List[float]:
    """
    Normalize a feature vector to zero mean and unit variance.
    Falls back to returning zeros if std is 0.
    """
    arr = np.array(features, dtype=np.float64)
    mean = np.mean(arr)
    std = np.std(arr)
    if std == 0:
        return [0.0] * len(features)
    return ((arr - mean) / std).tolist()


def compute_statistics(values: List[float]) -> Dict[str, float]:
    """
    Compute statistical features from a list of timing values.
    
    Returns: dict with mean, std, min, max, median, q25, q75
    """
    if not values:
        return {
            "mean": 0.0, "std": 0.0, "min": 0.0,
            "max": 0.0, "median": 0.0, "q25": 0.0, "q75": 0.0,
        }
    arr = np.array(values, dtype=np.float64)
    return {
        "mean": float(np.mean(arr)),
        "std": float(np.std(arr)),
        "min": float(np.min(arr)),
        "max": float(np.max(arr)),
        "median": float(np.median(arr)),
        "q25": float(np.percentile(arr, 25)),
        "q75": float(np.percentile(arr, 75)),
    }


def manhattan_distance(v1: List[float], v2: List[float]) -> float:
    """Compute Manhattan (L1) distance between two feature vectors."""
    a1 = np.array(v1, dtype=np.float64)
    a2 = np.array(v2, dtype=np.float64)
    return float(np.sum(np.abs(a1 - a2)))


def euclidean_distance(v1: List[float], v2: List[float]) -> float:
    """Compute Euclidean (L2) distance between two feature vectors."""
    a1 = np.array(v1, dtype=np.float64)
    a2 = np.array(v2, dtype=np.float64)
    return float(np.sqrt(np.sum((a1 - a2) ** 2)))


def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Compute cosine similarity between two feature vectors (0 to 1)."""
    a1 = np.array(v1, dtype=np.float64)
    a2 = np.array(v2, dtype=np.float64)
    dot = np.dot(a1, a2)
    norm1 = np.linalg.norm(a1)
    norm2 = np.linalg.norm(a2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return float(dot / (norm1 * norm2))
