"""Production-grade Vehicle Detection, Tracking, and Counting Orchestrator."""

import argparse
import logging
import os
import sys
import time
from pathlib import Path

# Safeguard console output for Unicode paths on Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add the parent directory to Python path to allow absolute imports of shared components
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

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
from vehicle_detection.counter import LineCrossingCounter
from vehicle_detection.utils import draw_hud, draw_tracks, export_events_to_csv

# Setup logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("smart_traffic.detect")


def run_pipeline(
    video_path: str,
    model_path: str = DEFAULT_MODEL,
    line_coords: str = None,
    show: bool = False,
    save: bool = False,
    export_csv: bool = False
):
    """
    Run the vehicle detection, tracking, and counting pipeline on a video file or camera stream.
    """
    logger.info("Initializing Smart Traffic pipeline...")

    # Determine if input source is a local webcam index
    video_source = video_path
    if video_path.isdigit():
        video_source = int(video_path)
        logger.info(f"Using camera stream index: {video_source}")
    else:
        logger.info(f"Using video file: {video_source}")

    # Initialize components
    try:
        detector = VehicleDetector(model_path)
        tracker = VehicleTracker(detector, TRACKER_TYPE)
        # Enable mock tracking if we are processing synthetic test files
        tracker.detect_mock_mode(video_path)
    except Exception as e:
        logger.critical(f"Initialization failed: {e}")
        return None

    # Open video capture
    cap = cv2.VideoCapture(video_source)
    if not cap.isOpened():
        logger.error(f"Cannot open video source: {video_path}")
        return None

    # Retrieve source video specs
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps_src = cap.get(cv2.CAP_PROP_FPS)
    if fps_src <= 0:
        fps_src = 30.0  # Fallback FPS

    # Parse or compute counting line coords
    # Default is horizontal line across the middle of the frame
    if line_coords:
        try:
            coords = list(map(int, line_coords.split(",")))
            line = ((coords[0], coords[1]), (coords[2], coords[3]))
        except Exception as e:
            logger.error(f"Failed to parse line coordinates '{line_coords}'. Using default. Error: {e}")
            line = ((0, height // 2), (width, height // 2))
    else:
        line = ((0, height // 2), (width, height // 2))

    counter = LineCrossingCounter(line)

    # Setup Video Writer if save is requested
    out_writer = None
    if save:
        video_name = "live_stream" if isinstance(video_source, int) else Path(video_path).stem
        out_video_path = OUTPUT_DIR / f"{video_name}_annotated.mp4"
        logger.info(f"Saving annotated video to: {out_video_path}")
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out_writer = cv2.VideoWriter(str(out_video_path), fourcc, fps_src, (width, height))

    # Frame processing loop metrics
    frame_count = 0
    total_inf_time = 0.0
    start_time = time.time()

    prev_frame_time = time.time()
    fps_display = 0.0

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1
            timestamp_sec = frame_count / fps_src

            # Calculate live FPS
            curr_frame_time = time.time()
            time_diff = curr_frame_time - prev_frame_time
            if time_diff > 0:
                fps_display = 1.0 / time_diff
            prev_frame_time = curr_frame_time

            # Perform object detection and tracking
            inf_start = time.time()
            tracks = tracker.track(
                frame,
                conf=CONF_THRESHOLD,
                iou=IOU_THRESHOLD
            )
            inf_end = time.time()
            inf_time_ms = (inf_end - inf_start) * 1000.0
            total_inf_time += inf_time_ms

            # Update line crossing and per-class counts
            counter.update(tracks, timestamp_sec)

            # Draw HUD and tracks onto frame
            draw_tracks(frame, tracks)
            draw_hud(frame, counter.get_counts(), fps_display, inf_time_ms, line)

            # Save annotated frame
            if out_writer:
                out_writer.write(frame)

            # Show live preview
            if show:
                cv2.imshow("Smart Traffic Management - Phase 2", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    logger.info("Video preview stopped by user ('q' key pressed).")
                    break

    except KeyboardInterrupt:
        logger.warning("Pipeline interrupted by user.")
    except Exception as e:
        logger.error(f"Error occurred during frame loop execution: {e}")
    finally:
        # Release resources
        cap.release()
        if out_writer:
            out_writer.release()
        if show:
            cv2.destroyAllWindows()

    total_time = time.time() - start_time
    avg_fps = frame_count / total_time if total_time > 0 else 0
    avg_inf = total_inf_time / frame_count if frame_count > 0 else 0

    # Print final counts in expected format
    print("\n--- Final Counts ---")
    for key in ("car", "bus", "truck", "motorcycle"):
        if key == "motorcycle":
            display = "Bikes"
        elif key == "bus":
            display = "Buses"
        else:
            display = f"{key.capitalize()}s"
        print(f"{display}: {counter.counts.get(key, 0)}")

    # Print evaluation metrics
    print("\n--- Performance Metrics ---")
    print(f"Total Frames: {frame_count}")
    print(f"Total Execution Time: {total_time:.2f} s")
    print(f"Average FPS: {avg_fps:.1f}")
    print(f"Average Inference Latency: {avg_inf:.1f} ms")
    total_vehicles = sum(counter.counts.values())
    print(f"Total Counted Vehicles: {total_vehicles}")

    # Export events to CSV
    if export_csv and counter.crossing_events:
        video_name = "live_stream" if isinstance(video_source, int) else Path(video_path).stem
        csv_filename = OUTPUT_DIR / f"{video_name}_detection_log.csv"
        export_events_to_csv(counter.crossing_events, str(csv_filename))

    return {
        "avg_fps": avg_fps,
        "avg_inference_ms": avg_inf,
        "total_vehicles": total_vehicles,
        "counts": dict(counter.counts),
        "frame_count": frame_count
    }


def main():
    parser = argparse.ArgumentParser(description="Modular vehicle detection and counting")
    parser.add_argument("--video", required=True, help="Path to video file or camera index (e.g., '0')")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Path to YOLO model weights")
    parser.add_argument("--line", default=None, help="Counting line as x1,y1,x2,y2 (e.g. 0,180,640,180)")
    parser.add_argument("--show", action="store_true", help="Display live preview screen")
    parser.add_argument("--save", action="store_true", help="Save annotated output video")
    parser.add_argument("--export-csv", action="store_true", help="Export logs of crossings to CSV")
    args = parser.parse_args()

    run_pipeline(
        video_path=args.video,
        model_path=args.model,
        line_coords=args.line,
        show=args.show,
        save=args.save,
        export_csv=args.export_csv
    )


if __name__ == "__main__":
    main()
