"""Lane geometry mapping and overlay rendering."""

import logging
import cv2
import numpy as np
from lane_detection.config import DEFAULT_LANE_POLYGONS, LANE_COLORS

logger = logging.getLogger(__name__)


class LaneDetector:
    """Manages lane geometries and checks if vehicles occupy specific lanes."""

    def __init__(self, lane_polygons: dict[str, list[tuple[int, int]]] = None):
        """
        Initialize LaneDetector with lane coordinates.

        Args:
            lane_polygons: Dict mapping lane name (e.g. 'A') to list of vertices.
        """
        polys = lane_polygons if lane_polygons else DEFAULT_LANE_POLYGONS
        self.lanes = {}
        # Pre-compile list of coordinates into numpy arrays for cv2 functions
        for name, coords in polys.items():
            self.lanes[name] = np.array(coords, dtype=np.int32)
        logger.info(f"LaneDetector initialized with lanes: {list(self.lanes.keys())}")

    def get_lane_for_point(self, point: tuple[float, float]) -> str | None:
        """
        Determine which lane contains the given point (centroid).

        Args:
            point: (x, y) coordinates of the vehicle centroid.

        Returns:
            The lane name (e.g. 'A', 'B', 'C', 'D') or None if outside all lanes.
        """
        x, y = float(point[0]), float(point[1])
        for name, contour in self.lanes.items():
            # pointPolygonTest returns >= 0 if point is inside or on the contour
            if cv2.pointPolygonTest(contour, (x, y), False) >= 0:
                return name
        return None

    def draw_lanes(self, frame, alpha: float = 0.15):
        """
        Draw translucent colored overlays for each lane and overlay their labels.

        Args:
            frame: OpenCV image frame to draw on.
            alpha: Transparency factor (0.0 = invisible, 1.0 = solid).
        """
        overlay = frame.copy()

        for name, contour in self.lanes.items():
            color = LANE_COLORS.get(name, (128, 128, 128))

            # Draw translucent fill
            cv2.fillPoly(overlay, [contour], color)

            # Draw boundary line
            cv2.polylines(frame, [contour], True, color, 2)

            # Draw label in the center/centroid of the lane polygon
            M = cv2.moments(contour)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
            else:
                x, y, w, h = cv2.boundingRect(contour)
                cx, cy = x + w // 2, y + h // 2

            # Render text label with dark background box for readability
            label = f"Lane {name}"
            (text_w, text_h), baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            cv2.rectangle(
                frame,
                (cx - text_w // 2 - 5, cy - text_h - 5),
                (cx + text_w // 2 + 5, cy + 5),
                (30, 30, 30),
                -1
            )
            cv2.putText(
                frame,
                label,
                (cx - text_w // 2, cy - 2),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                1,
                cv2.LINE_AA
            )

        # Blend the filled polygons with the original frame
        cv2.addWeighted(overlay, alpha, frame, 1.0 - alpha, 0, frame)
