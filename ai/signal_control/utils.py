"""Visual drawing overlays and CSV export logging for signal control."""

import csv
import logging
import os
import cv2
from lane_detection.config import LANE_COLORS
from signal_control.config import SIGNAL_TIMINGS
from signal_control.density import classify_density

logger = logging.getLogger(__name__)


def draw_signal_hud(
    frame,
    lane_counts: dict[str, int],
    controller,
    fps: float,
    inference_ms: float
):
    """Draw a professional HUD overlay displaying counts, density, active signals, and countdowns."""
    h, w = frame.shape[:2]

    # Semi-transparent background overlay for the dashboard HUD (top right)
    hud_w = 280
    hud_h = 230
    overlay = frame.copy()
    cv2.rectangle(overlay, (w - 10 - hud_w, 10), (w - 10, 10 + hud_h), (30, 30, 30), -1)
    cv2.addWeighted(overlay, 0.75, frame, 0.25, 0, frame)

    # Header
    cv2.putText(
        frame,
        "ADAPTIVE SIGNAL CONTROL",
        (w - hud_w, 32),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (255, 255, 255),
        2,
        cv2.LINE_AA
    )
    cv2.line(frame, (w - hud_w, 38), (w - 20, 38), (100, 100, 100), 1)

    y_offset = 58
    for name in ["A", "B", "C", "D"]:
        count = lane_counts.get(name, 0)
        density = classify_density(count)

        # Determine signal color for this lane
        # If this is the active green lane, match the controller state
        if name == controller.current_green_lane:
            if controller.signal_state == "Green":
                light_color = (0, 255, 0)  # Green
            elif controller.signal_state == "Yellow":
                light_color = (0, 255, 255)  # Yellow
            else:
                light_color = (0, 0, 255)  # Red
        else:
            light_color = (0, 0, 255)  # Red (all other lanes are red)

        # Draw a physical circle representing the traffic signal light
        cv2.circle(frame, (w - hud_w + 15, y_offset - 4), 6, light_color, -1)
        cv2.circle(frame, (w - hud_w + 15, y_offset - 4), 6, (255, 255, 255), 1)

        # Draw text mapping count + density
        lane_color = LANE_COLORS.get(name, (128, 128, 128))
        # Draw small lane badge
        cv2.rectangle(frame, (w - hud_w + 30, y_offset - 10), (w - hud_w + 42, y_offset + 2), lane_color, -1)
        cv2.rectangle(frame, (w - hud_w + 30, y_offset - 10), (w - hud_w + 42, y_offset + 2), (255, 255, 255), 1)

        cv2.putText(
            frame,
            f"Lane {name}: {count} ({density})",
            (w - hud_w + 50, y_offset),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            (255, 255, 255),
            1,
            cv2.LINE_AA
        )
        y_offset += 22

    # Draw Current Green Lane, Countdown, and State details
    cv2.line(frame, (w - hud_w, y_offset - 10), (w - 20, y_offset - 10), (100, 100, 100), 1)

    active_text = f"Green Lane: {controller.current_green_lane or 'None'}"
    cv2.putText(
        frame,
        active_text,
        (w - hud_w + 10, y_offset + 5),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.45,
        (255, 255, 255),
        1,
        cv2.LINE_AA
    )

    timer_text = f"Timer: {controller.timer_countdown:.1f}s"
    cv2.putText(
        frame,
        timer_text,
        (w - hud_w + 10, y_offset + 25),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.45,
        (255, 255, 255),
        1,
        cv2.LINE_AA
    )

    state_color = (0, 0, 255)  # Red default
    if controller.signal_state == "Green":
        state_color = (0, 255, 0)
    elif controller.signal_state == "Yellow":
        state_color = (0, 255, 255)

    cv2.putText(
        frame,
        "Signal: ",
        (w - hud_w + 10, y_offset + 45),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.45,
        (255, 255, 255),
        1,
        cv2.LINE_AA
    )
    cv2.putText(
        frame,
        controller.signal_state.upper(),
        (w - hud_w + 70, y_offset + 45),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.45,
        state_color,
        2,
        cv2.LINE_AA
    )

    # Draw stats bottom left (Performance)
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
        f"Inference: {inference_ms:.1f} ms",
        (20, h - 22),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (255, 255, 0),
        1,
        cv2.LINE_AA
    )


def export_signal_history_to_csv(history: list[dict], csv_path: str):
    """
    Export historical time-series signal logs to a CSV file.

    Args:
        history: List of dicts representing signal states per frame.
        csv_path: Destination CSV file path.
    """
    try:
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)
        with open(csv_path, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([
                "Timestamp",
                "Lane",
                "Vehicle Count",
                "Density",
                "Assigned Green Time",
                "Signal Status"
            ])

            for row in history:
                writer.writerow([
                    f"{row['timestamp']:.2f}",
                    row["lane"],
                    row["count"],
                    row["density"],
                    row["assigned_green_time"],
                    row["status"]
                ])

        logger.info(f"Successfully exported adaptive signal log to CSV: {csv_path}")
    except Exception as e:
        logger.error(f"Failed to export signal logs to CSV: {e}")
