"""Accident detection — Phase 7."""

from collections import deque


class AccidentDetector:
    """Detect sudden stops and stationary clusters as potential accidents."""

    def __init__(self, speed_threshold: float = 2.0, stationary_frames: int = 30):
        self.speed_threshold = speed_threshold
        self.stationary_frames = stationary_frames
        self.track_history: dict[int, deque] = {}

    def update(self, track_id: int, center: tuple[float, float]) -> bool:
        if track_id not in self.track_history:
            self.track_history[track_id] = deque(maxlen=self.stationary_frames)

        history = self.track_history[track_id]
        history.append(center)

        if len(history) < self.stationary_frames:
            return False

        # Check if vehicle barely moved over window
        xs = [p[0] for p in history]
        ys = [p[1] for p in history]
        movement = ((max(xs) - min(xs)) ** 2 + (max(ys) - min(ys)) ** 2) ** 0.5
        return movement < self.speed_threshold

    def reset(self, track_id: int):
        self.track_history.pop(track_id, None)


def create_alert(accident_type: str, location: str, camera_id: str) -> dict:
    return {
        "type": "accident",
        "accident_type": accident_type,
        "location": location,
        "camera_id": camera_id,
        "message": f"Accident Detected: {accident_type} at {location}",
    }
