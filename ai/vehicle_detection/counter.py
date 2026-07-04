"""Line crossing vehicle counter."""

import logging
from collections import defaultdict
from shared.constants import VEHICLE_CLASSES, CLASS_DISPLAY
from vehicle_detection.utils import intersect

logger = logging.getLogger(__name__)


class LineCrossingCounter:
    """Tracks and counts vehicles crossing a predefined line to avoid duplicates."""

    def __init__(self, line_coords: tuple[tuple[float, float], tuple[float, float]]):
        """
        Initialize the counter.

        Args:
            line_coords: A tuple of two points defining the line: ((x1, y1), (x2, y2))
        """
        self.line = line_coords
        self.counted_ids = set()
        self.track_history = {}  # track_id -> previous centroid (cx, cy)
        # Store counts per class name (e.g. "car", "bus", etc.)
        self.counts = defaultdict(int)
        self.crossing_events = []  # List of dicts recording each crossing
        logger.info(f"LineCrossingCounter initialized with line: {line_coords}")

    def update(self, tracks: list[dict], timestamp_sec: float) -> list[dict]:
        """
        Update tracking history and check for line crossings.

        Args:
            tracks: List of active track dictionaries from the tracker.
            timestamp_sec: Current frame timestamp in seconds.

        Returns:
            A list of new crossing event dicts detected in this update.
        """
        new_crossings = []
        active_ids = set()

        for track in tracks:
            track_id = track["id"]
            active_ids.add(track_id)
            bbox = track["bbox"]
            cls_id = track["cls"]
            cls_name = VEHICLE_CLASSES.get(cls_id, "unknown")

            # Compute centroid of bounding box
            cx = (bbox[0] + bbox[2]) / 2.0
            cy = (bbox[1] + bbox[3]) / 2.0
            current_centroid = (cx, cy)

            # Check if we have history for this track
            if track_id in self.track_history:
                prev_centroid = self.track_history[track_id]

                # Check if the track crossed the counting line
                # Segment AB = prev_centroid -> current_centroid
                # Segment CD = self.line[0] -> self.line[1]
                if track_id not in self.counted_ids:
                    if intersect(prev_centroid, current_centroid, self.line[0], self.line[1]):
                        # Crossed!
                        self.counted_ids.add(track_id)
                        self.counts[cls_name] += 1

                        # Determine direction
                        # A = prev, B = current, C = line_start, D = line_end
                        ax, ay = prev_centroid
                        bx, by = current_centroid
                        cx_l, cy_l = self.line[0]
                        dx_l, dy_l = self.line[1]

                        # Vector V = B - A
                        vx, vy = bx - ax, by - ay
                        # Normal vector N = (-(dy - cy), dx - cx)
                        nx, ny = -(dy_l - cy_l), dx_l - cx_l

                        # Dot product V . N
                        dot_product = vx * nx + vy * ny
                        direction = "inbound" if dot_product >= 0 else "outbound"

                        event = {
                            "timestamp": timestamp_sec,
                            "track_id": track_id,
                            "class": cls_name,
                            "direction": direction,
                        }
                        self.crossing_events.append(event)
                        new_crossings.append(event)

                        logger.info(
                            f"Vehicle Crossed: ID {track_id} | Class: {cls_name} | "
                            f"Direction: {direction} | Total: {dict(self.counts)}"
                        )

            # Update history
            self.track_history[track_id] = current_centroid

        # Clean up track history for inactive IDs to prevent memory leaks
        inactive_ids = set(self.track_history.keys()) - active_ids
        for inactive_id in inactive_ids:
            # We keep the counted_ids to prevent recount if it reappears,
            # but delete the history
            del self.track_history[inactive_id]

        return new_crossings

    def get_counts(self) -> dict[str, int]:
        """Return counts of vehicles per class."""
        return dict(self.counts)
