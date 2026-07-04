"""Adaptive signal controller and density classification CLI orchestrator."""

import argparse
import logging
import os
import sys
import time
from pathlib import Path

# Add the parent directory to Python path to allow absolute imports of shared components
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Safeguard console output for Unicode paths on Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

import cv2

from vehicle_detection.config import (
    CONF_THRESHOLD,
    IOU_THRESHOLD,
    DEFAULT_MODEL,
    TRACKER_TYPE,
    OUTPUT_DIR
)
from vehicle_detection.detector import VehicleDetector
from vehicle_detection.tracker import VehicleTracker
from lane_detection.lane_detector import LaneDetector
from lane_detection.lane_manager import LaneManager
from signal_control.config import SIGNAL_TIMINGS
from signal_control.density import classify_density
from signal_control.signal_controller import AdaptiveSignalController
from signal_control.utils import draw_signal_hud, export_signal_history_to_csv

# Setup logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("smart_traffic.signal_detect")


def run_signal_pipeline(
    video_path: str,
    model_path: str = DEFAULT_MODEL,
    show: bool = False,
    save: bool = False,
    export_csv: bool = False
):
    """Run integrated vehicle tracking + lane segmentation + adaptive signal pipeline."""
    logger.info("Initializing integrated Adaptive Signal Control pipeline...")

    video_source = video_path
    if video_path.isdigit():
        video_source = int(video_path)
        logger.info(f"Using camera stream index: {video_source}")
    else:
        logger.info(f"Using video file: {video_source}")

    # Load tracker and detector
    try:
        detector = VehicleDetector(model_path)
        tracker = VehicleTracker(detector, TRACKER_TYPE)
        # Check and enable mock tracking if synthetic test video is loaded
        tracker.detect_mock_mode(video_path)
    except Exception as e:
        logger.critical(f"Detector/Tracker initialization failed: {e}")
        return None

    # Open video capture
    cap = cv2.VideoCapture(video_source)
    if not cap.isOpened():
        logger.error(f"Cannot open video source: {video_path}")
        return None

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps_src = cap.get(cv2.CAP_PROP_FPS)
    if fps_src <= 0:
        fps_src = 30.0

    # Initialize Lane Components
    lane_polygons = None
    if width != 640 or height != 360:
        w_step = width // 4
        lane_polygons = {
            "A": [(0, 0), (w_step, 0), (w_step, height), (0, height)],
            "B": [(w_step, 0), (w_step * 2, 0), (w_step * 2, height), (w_step, height)],
            "C": [(w_step * 2, 0), (w_step * 3, 0), (w_step * 3, height), (w_step * 2, height)],
            "D": [(w_step * 3, 0), (width, 0), (width, height), (w_step * 3, height)],
        }

    lane_detector = LaneDetector(lane_polygons)
    lane_manager = LaneManager(["A", "B", "C", "D"])
    signal_controller = AdaptiveSignalController(["A", "B", "C", "D"])

    # Setup Video Writer
    out_writer = None
    if save:
        video_name = "live_stream" if isinstance(video_source, int) else Path(video_path).stem
        out_video_path = OUTPUT_DIR / f"{video_name}_signals_annotated.mp4"
        logger.info(f"Saving annotated video to: {out_video_path}")
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out_writer = cv2.VideoWriter(str(out_video_path), fourcc, fps_src, (width, height))

    frame_count = 0
    total_inf_time = 0.0
    start_time = time.time()

    prev_frame_time = time.time()
    fps_display = 0.0

    # History buffer for CSV export
    signal_history = []

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1
            timestamp_sec = frame_count / fps_src
            elapsed_frame_time = 1.0 / fps_src

            curr_frame_time = time.time()
            time_diff = curr_frame_time - prev_frame_time
            if time_diff > 0:
                fps_display = 1.0 / time_diff
            prev_frame_time = curr_frame_time

            # Tracking inference
            inf_start = time.time()
            tracks = tracker.track(
                frame,
                conf=CONF_THRESHOLD,
                iou=IOU_THRESHOLD
            )
            inf_end = time.time()
            inf_time_ms = (inf_end - inf_start) * 1000.0
            total_inf_time += inf_time_ms

            # Map tracking boxes to lanes
            lane_manager.update(tracks, lane_detector, frame_count, timestamp_sec)
            lane_counts = lane_manager.get_live_counts()

            # Update Adaptive Signal controller state
            signal_controller.update(lane_counts, elapsed_frame_time)

            # Record metrics for all lanes in history buffer
            for lane in ["A", "B", "C", "D"]:
                count = lane_counts.get(lane, 0)
                density = classify_density(count)

                # Determine status and dynamic time
                status = "RED"
                assigned_green = 0
                if lane == signal_controller.current_green_lane:
                    status = signal_controller.signal_state.upper()
                    assigned_green = signal_controller.get_green_duration(count)

                signal_history.append({
                    "timestamp": timestamp_sec,
                    "lane": lane,
                    "count": count,
                    "density": density,
                    "assigned_green_time": assigned_green,
                    "status": status,
                })

            # Render visuals
            lane_detector.draw_lanes(frame)
            from lane_detection.detect_lanes import draw_vehicle_tags_with_lanes
            draw_vehicle_tags_with_lanes(frame, tracks)
            draw_signal_hud(
                frame,
                lane_counts,
                signal_controller,
                fps_display,
                inf_time_ms
            )

            # Save annotated frame
            if out_writer:
                out_writer.write(frame)

            # Live preview screen
            if show:
                cv2.imshow("Smart Traffic Management - Phase 4 (Signals)", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    logger.info("Video preview stopped by user.")
                    break

    except KeyboardInterrupt:
        logger.warning("Pipeline interrupted by user.")
    except Exception as e:
        logger.error(f"Error executing frame loop: {e}")
    finally:
        cap.release()
        if out_writer:
            out_writer.release()
        if show:
            cv2.destroyAllWindows()

    total_time = time.time() - start_time
    avg_fps = frame_count / total_time if total_time > 0 else 0
    avg_inf = total_inf_time / frame_count if frame_count > 0 else 0

    print("\n--- Final Controller State ---")
    print(f"Current Active Lane: {signal_controller.current_green_lane or 'None'}")
    print(f"Current Signal State: {signal_controller.signal_state.upper()}")
    print(f"Remaining Countdown: {signal_controller.timer_countdown:.1f}s")
    print(f"Starvation Cycle Wait Counts: {dict(signal_controller.cycles_waiting)}")

    print("\n--- Performance Metrics ---")
    print(f"Total Frames: {frame_count}")
    print(f"Total Execution Time: {total_time:.2f} s")
    print(f"Average FPS: {avg_fps:.1f}")
    print(f"Average Processing Latency: {avg_inf:.1f} ms")

    # Save CSV
    if export_csv and signal_history:
        video_name = "live_stream" if isinstance(video_source, int) else Path(video_path).stem
        csv_filename = OUTPUT_DIR / f"{video_name}_signal_logs.csv"
        export_signal_history_to_csv(signal_history, str(csv_filename))

    return {
        "avg_fps": avg_fps,
        "avg_inference_ms": avg_inf,
        "frame_count": frame_count,
        "final_lane": signal_controller.current_green_lane,
        "final_state": signal_controller.signal_state
    }


def main():
    parser = argparse.ArgumentParser(description="Adaptive signal control with density classification")
    parser.add_argument("--video", required=True, help="Path to video file or camera index (e.g. '0')")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Path to YOLO model weights")
    parser.add_argument("--show", action="store_true", help="Display live preview screen")
    parser.add_argument("--save", action="store_true", help="Save annotated output video")
    parser.add_argument("--export-csv", action="store_true", help="Export signal logs to CSV")
    args = parser.parse_args()

    run_signal_pipeline(
        video_path=args.video,
        model_path=args.model,
        show=args.show,
        save=args.save,
        export_csv=args.export_csv
    )


if __name__ == "__main__":
    main()
