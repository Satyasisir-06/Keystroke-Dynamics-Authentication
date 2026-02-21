"""
KeyAuth - Feature Extraction Engine
Computes behavioral biometric features from raw keystroke data.

Features extracted:
  - Dwell times (how long each key is held)
  - Flight times (time between releasing one key and pressing next)
  - Digraph latencies (key-to-key press intervals)
  - Typing speed (characters per second)
  - Statistical features (mean, std, min, max, median)
  - Mobile extras: pressure stats, touch size stats
"""
from typing import List, Dict
from app.schemas import KeystrokeEvent
from app.ml.utils import compute_statistics


def extract_features(keystrokes: List[KeystrokeEvent]) -> Dict:
    """
    Extract a comprehensive feature vector from raw keystroke events.
    
    Args:
        keystrokes: List of KeystrokeEvent objects with press/release times
    
    Returns:
        Dict containing:
          - 'vector': flat list of floats (the feature vector for ML)
          - 'details': human-readable breakdown of features
          - 'dwell_times': list of dwell times
          - 'flight_times': list of flight times
          - 'typing_speed': chars per second
    """
    if len(keystrokes) < 2:
        raise ValueError("Need at least 2 keystrokes to extract features")

    # ── Dwell Times ─────────────────────────────────────────────
    # How long each key is held down (release - press)
    dwell_times = []
    for ks in keystrokes:
        dwell = ks.release_time - ks.press_time
        if dwell > 0:
            dwell_times.append(dwell)

    # ── Flight Times ────────────────────────────────────────────
    # Time between releasing one key and pressing the next
    flight_times = []
    for i in range(1, len(keystrokes)):
        flight = keystrokes[i].press_time - keystrokes[i - 1].release_time
        flight_times.append(flight)

    # ── Digraph Latencies ───────────────────────────────────────
    # Time between pressing one key and pressing the next (press-to-press)
    digraph_latencies = []
    for i in range(1, len(keystrokes)):
        latency = keystrokes[i].press_time - keystrokes[i - 1].press_time
        digraph_latencies.append(latency)

    # ── Typing Speed ────────────────────────────────────────────
    if len(keystrokes) >= 2:
        total_time_ms = keystrokes[-1].release_time - keystrokes[0].press_time
        total_time_sec = max(total_time_ms / 1000.0, 0.001)
        typing_speed = len(keystrokes) / total_time_sec
    else:
        typing_speed = 0.0

    # ── Statistical Features ────────────────────────────────────
    dwell_stats = compute_statistics(dwell_times)
    flight_stats = compute_statistics(flight_times)
    digraph_stats = compute_statistics(digraph_latencies)

    # ── Mobile Features (pressure & touch size) ─────────────────
    pressures = [ks.pressure for ks in keystrokes if ks.pressure is not None]
    touch_sizes = [ks.touch_size for ks in keystrokes if ks.touch_size is not None]
    pressure_stats = compute_statistics(pressures) if pressures else compute_statistics([])
    touch_stats = compute_statistics(touch_sizes) if touch_sizes else compute_statistics([])

    # ── Build Feature Vector ────────────────────────────────────
    # Consistent ordering for ML model input
    feature_vector = [
        # Dwell time stats (7 features)
        dwell_stats["mean"],
        dwell_stats["std"],
        dwell_stats["min"],
        dwell_stats["max"],
        dwell_stats["median"],
        dwell_stats["q25"],
        dwell_stats["q75"],
        # Flight time stats (7 features)
        flight_stats["mean"],
        flight_stats["std"],
        flight_stats["min"],
        flight_stats["max"],
        flight_stats["median"],
        flight_stats["q25"],
        flight_stats["q75"],
        # Digraph latency stats (7 features)
        digraph_stats["mean"],
        digraph_stats["std"],
        digraph_stats["min"],
        digraph_stats["max"],
        digraph_stats["median"],
        digraph_stats["q25"],
        digraph_stats["q75"],
        # Speed (1 feature)
        typing_speed,
        # Pressure stats (7 features)
        pressure_stats["mean"],
        pressure_stats["std"],
        pressure_stats["min"],
        pressure_stats["max"],
        pressure_stats["median"],
        pressure_stats["q25"],
        pressure_stats["q75"],
        # Touch size stats (7 features)
        touch_stats["mean"],
        touch_stats["std"],
        touch_stats["min"],
        touch_stats["max"],
        touch_stats["median"],
        touch_stats["q25"],
        touch_stats["q75"],
    ]
    # Total: 36 features

    details = {
        "dwell_time_mean": round(dwell_stats["mean"], 2),
        "dwell_time_std": round(dwell_stats["std"], 2),
        "flight_time_mean": round(flight_stats["mean"], 2),
        "flight_time_std": round(flight_stats["std"], 2),
        "digraph_latency_mean": round(digraph_stats["mean"], 2),
        "typing_speed": round(typing_speed, 2),
        "pressure_mean": round(pressure_stats["mean"], 4),
        "touch_size_mean": round(touch_stats["mean"], 4),
        "feature_count": len(feature_vector),
    }

    return {
        "vector": feature_vector,
        "details": details,
        "dwell_times": dwell_times,
        "flight_times": flight_times,
        "typing_speed": typing_speed,
    }
