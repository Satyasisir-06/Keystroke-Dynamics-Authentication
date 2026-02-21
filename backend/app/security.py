"""
KeyAuth - Security Module
Encryption, anti-replay protection, and rate limiting helpers
"""
import hashlib
import time
from typing import Dict, Optional
from collections import defaultdict


class AntiReplayGuard:
    """
    Prevents replay attacks by tracking recent keystroke submission hashes.
    Each submission is hashed and stored with a timestamp.
    Duplicate submissions within the window are rejected.
    """

    def __init__(self, window_seconds: int = 300):
        self.window = window_seconds
        self._cache: Dict[str, float] = {}

    def _hash_keystrokes(self, keystrokes_data: list) -> str:
        """Create a hash of keystroke data for deduplication."""
        raw = str([(k.key, k.press_time, k.release_time) for k in keystrokes_data])
        return hashlib.sha256(raw.encode()).hexdigest()

    def check_and_record(self, keystrokes_data: list) -> bool:
        """
        Check if this submission is a replay. Records it if new.
        
        Returns True if the submission is VALID (not a replay).
        Returns False if it's a duplicate (replay attack).
        """
        self._cleanup()
        submission_hash = self._hash_keystrokes(keystrokes_data)

        if submission_hash in self._cache:
            return False  # Replay detected

        self._cache[submission_hash] = time.time()
        return True

    def _cleanup(self):
        """Remove expired entries from the cache."""
        now = time.time()
        expired = [k for k, v in self._cache.items() if now - v > self.window]
        for k in expired:
            del self._cache[k]


class RateLimiter:
    """
    Simple in-memory rate limiter per username.
    Limits authentication attempts to prevent brute force.
    """

    def __init__(self, max_attempts: int = 10, window_seconds: int = 60):
        self.max_attempts = max_attempts
        self.window = window_seconds
        self._attempts: Dict[str, list] = defaultdict(list)

    def is_allowed(self, username: str) -> bool:
        """Check if the user is allowed to make another attempt."""
        now = time.time()
        # Clean old attempts
        self._attempts[username] = [
            t for t in self._attempts[username] if now - t < self.window
        ]
        return len(self._attempts[username]) < self.max_attempts

    def record_attempt(self, username: str):
        """Record an authentication attempt."""
        self._attempts[username].append(time.time())

    def remaining_attempts(self, username: str) -> int:
        """Get remaining attempts for a user."""
        now = time.time()
        self._attempts[username] = [
            t for t in self._attempts[username] if now - t < self.window
        ]
        return max(0, self.max_attempts - len(self._attempts[username]))


# Global instances
anti_replay = AntiReplayGuard(window_seconds=300)
rate_limiter = RateLimiter(max_attempts=10, window_seconds=60)
