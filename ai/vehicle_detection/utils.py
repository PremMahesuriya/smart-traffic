"""Utility mathematical, drawing, and CSV logging helpers."""

import csv
import logging
import os
import cv2
from shared.constants import CLASS_DISPLAY, VEHICLE_CLASSES

logger = logging.getLogger(__name__)

# Colors mapping (BGR format for OpenCV)
CLASS_COLORS = {
    "car": (255, 165, 0),       # Orange
    "motorcycle": (0, 255, 255),  # Yellow / Bike
    "bus": (255, 0, 255),       # Magenta
    "truck": (0, 0, 255),        # Red
    "unknown": (128, 128, 128)  # Gray
}


def ccw(A: tuple[float, float], B: tuple[float, float], C: tuple[float, float]) -> bool:
    """Check if points A, B, C are in counter-clockwise order."""
    return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])


def intersect(A: tuple[float, float], B: tuple[float, float], C: tuple[float, float], D: tuple[float, float]) -> bool:
    """Return True if line segment AB intersects segment CD."""
    return ccw(A, C, D) != ccw(B, C, D) and ccw(A, B, C) != ccw(A, B, D)


def draw_hud(frame, counts: dict[str, int], fps: float, inference_time_ms: float, line: tuple[tuple[int, int], tuple[int, int]]):
    """Draw a clean, professional HUD containing counts and performance metrics."""
    h, w = frame.shape[:2]

    # Draw counting line
    pt1, pt2 = line
    cv2.line(frame, pt1, pt2, (0, 0, 255), 2)  # Red line
    # Add small "COUNTING LINE" label
    cv2.putText(
        frame,
        "COUNTING LINE",
        (pt1[0] + 10, pt1[1] - 8),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (0, 0, 255),
        1,
        cv2.LINE_AA
    )

    # Semi-transparent background overlay for the dashboard HUD (top left)
    hud_w = 220
    hud_h = 150
    overlay = frame.copy()
    cv2.rectangle(overlay, (10, 10), (10 + hud_w, 10 + hud_h), (30, 30, 30), -1)
    # Blend overlay (alpha = 0.7)
    cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)

    # Draw HUD text
    cv2.putText(frame, "TRAFFIC METRICS", (20, 32), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.line(frame, (20, 38), (10 + hud_w - 10, 38), (100, 100, 100), 1)

    y_offset = 58
    for cls_name in ["car", "bus", "truck", "motorcycle"]:
        display = CLASS_DISPLAY.get(cls_name, cls_name.capitalize())
        count = counts.get(cls_name, 0)
        cv2.putText(
            frame,
            f"{display}: {count}",
            (20, y_offset),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            1,
            cv2.LINE_AA
        )
        y_offset += 20

    # Draw Performance Stats (bottom left)
    perf_w = 180
    perf_h = 55
    overlay_perf = frame.copy()
    cv2.rectangle(overlay_perf, (10, h - 10 - perf_h), (10 + perf_w, h - 10), (30, 30, 30), -1)
    cv2.addWeighted(overlay_perf, 0.7, frame, 0.3, 0, frame)

    cv2.putText(
        frame,
        f"FPS: {fps:.1f}",
        (20, h - 42),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (0, 255, 0),
        1,
        cv2.LINE_AA
    )
    cv2.putText(
        frame,
        f"Inference: {inference_time_ms:.1f} ms",
        (20, h - 22),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (255, 255, 0),
        1,
        cv2.LINE_AA
    )


def draw_tracks(frame, tracks: list[dict]):
    """Draw bounding boxes, confidence, class, and persistent tracking ID."""
    for track in tracks:
        bbox = track["bbox"]
        track_id = track["id"]
        cls_id = track["cls"]
        conf = track["conf"]

        cls_name = VEHICLE_CLASSES.get(cls_id, "unknown")
        color = CLASS_COLORS.get(cls_name, CLASS_COLORS["unknown"])
        display_name = CLASS_DISPLAY.get(cls_name, cls_name.capitalize())

        x1, y1, x2, y2 = map(int, bbox)

        # Draw bounding box
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

        # Draw a tag tab above the bounding box
        label = f"{display_name} #{track_id} [Conf: {conf:.2f}]"
        (label_w, label_h), baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)
        cv2.rectangle(frame, (x1, y1 - label_h - 10), (x1 + label_w + 10, y1), color, -1)
        cv2.putText(
            frame,
            label,
            (x1 + 5, y1 - 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.4,
            (255, 255, 255) if sum(color) < 400 else (0, 0, 0),
            1,
            cv2.LINE_AA
        )


def export_events_to_csv(events: list[dict], csv_path: str):
    """
    Export crossing event list to a CSV file.

    Args:
        events: List of dicts representing events
        csv_path: Destination file path
    """
    try:
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)
        # Write to file
        with open(csv_path, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Timestamp", "TrackID", "Class", "Direction"])
            for e in events:
                writer.writerow([
                    f"{e['timestamp']:.2f}",
                    e["track_id"],
                    e["class"],
                    e["direction"]
                ])
        logger.info(f"Successfully exported {len(events)} events to CSV: {csv_path}")
    except Exception as e:
        logger.error(f"Failed to export events to CSV: {e}")
