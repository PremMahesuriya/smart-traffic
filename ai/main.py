"""Main Smart Traffic Management pipeline orchestrator.

Integrates detection, tracking, lane occupancy mapping, adaptive signal control,
performance monitoring, and sends real-time updates to the Express backend.
"""

import argparse
import logging
import os
import sys
import time
from pathlib import Path

# Add the parent directory to Python path to allow absolute imports
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Ensure output streams are configured for UTF-8 on Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

import cv2

# Optional hardware profiling packages
try:
    import psutil
except ImportError:
    psutil = None

# Optional HTTP posting library
try:
    import requests
except ImportError:
    requests = None

# Import modular components from existing phases
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
logger = logging.getLogger("smart_traffic.main_pipeline")


def get_hardware_telemetry() -> tuple[float, float]:
    """Measure CPU and RAM usage metrics using psutil."""
    cpu_usage = 0.0
    mem_usage_mb = 0.0
    if psutil:
        try:
            # Get process-specific metrics
            proc = psutil.Process(os.getpid())
            cpu_usage = proc.cpu_percent(interval=None)
            mem_usage_mb = proc.memory_info().rss / (1024 * 1024)
        except Exception:
            pass
    return cpu_usage, mem_usage_mb


def post_telemetry_to_backend(url: str, payload: dict):
    """Post real-time traffic status updates as a JSON payload to the Express REST API."""
    if not requests:
        logger.warning("Requests package is missing. Bypassing backend HTTP update.")
        return

    try:
        # Send POST request to backend internal endpoint
        res = requests.post(f"{url}/api/internal/updateTraffic", json=payload, timeout=2.0)
        if res.status_code == 200:
            logger.info(f"Successfully sent live frame telemetry update to backend (time: {payload['timestamp']:.2f}s)")
        else:
            logger.warning(f"Backend update failed with status code: {res.status_code}")
    except Exception as e:
        logger.error(f"Cannot connect to backend REST API: {e}")


def run_pipeline(
    video_path: str,
    model_path: str = DEFAULT_MODEL,
    backend_url: str = "http://localhost:5000",
    show: bool = False,
    save: bool = False,
    export_csv: bool = False,
    post_interval_frames: int = 15  # Post telemetry update every N frames to optimize DB
):
    """Execute integrated vehicle tracking + lane mapping + adaptive signals + backend post pipeline."""
    logger.info("Starting integrated Main AI Traffic Pipeline...")
    logger.info(f"Video input: {video_path} | Backend REST API: {backend_url}")

    # Determine input stream type
    video_source = video_path
    if video_path.isdigit():
        video_source = int(video_path)

    # Initialize YOLO detector & tracker
    try:
        detector = VehicleDetector(model_path)
        tracker = VehicleTracker(detector, TRACKER_TYPE)
        # Enable mock tracks mapping if using synthetic test videos
        tracker.detect_mock_mode(video_path)
    except Exception as e:
        logger.critical(f"Failed to initialize detector/tracker: {e}")
        return False

    cap = cv2.VideoCapture(video_source)
    if not cap.isOpened():
        logger.error(f"Failed to open video source: {video_path}")
        return False

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps_src = cap.get(cv2.CAP_PROP_FPS) or 30.0

    # Configure custom lane polygons based on frame size
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

    # Configure video writer
    out_writer = None
    if save:
        video_name = "live_camera" if isinstance(video_source, int) else Path(video_path).stem
        out_video_path = OUTPUT_DIR / f"{video_name}_main_output.mp4"
        logger.info(f"Saving output video to: {out_video_path}")
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out_writer = cv2.VideoWriter(str(out_video_path), fourcc, fps_src, (width, height))

    frame_count = 0
    total_inf_time = 0.0
    start_time = time.time()
    prev_frame_time = time.time()
    fps_display = 0.0

    # CSV log history array
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

            # 1. Run YOLO detection & ByteTrack tracking
            inf_start = time.time()
            tracks = tracker.track(frame, conf=CONF_THRESHOLD, iou=IOU_THRESHOLD)
            inf_end = time.time()
            inf_time_ms = (inf_end - inf_start) * 1000.0
            total_inf_time += inf_time_ms

            # 2. Map coordinates to lanes and update counts
            lane_manager.update(tracks, lane_detector, frame_count, timestamp_sec)
            lane_counts = lane_manager.get_live_counts()

            # 3. Update Adaptive Traffic Signal timings
            signal_controller.update(lane_counts, elapsed_frame_time)

            # 4. Measure hardware usage metrics
            cpu_usage, mem_usage_mb = get_hardware_telemetry()

            # Format signal state variables
            sig_state = signal_controller.signal_state.upper()
            sig_lane = signal_controller.current_green_lane or "None"
            sig_green_time = signal_controller.get_green_duration(lane_counts.get(sig_lane, 0)) if sig_lane != "None" else 0
            sig_rem_time = signal_controller.timer_countdown

            # 5. Send real-time updates directly to backend (JSON payload)
            if frame_count % post_interval_frames == 0 or frame_count == 1:
                densities = {lane: classify_density(lane_counts.get(lane, 0)) for lane in ["A", "B", "C", "D"]}
                payload = {
                    "timestamp": timestamp_sec,
                    "laneCounts": lane_counts,
                    "densities": densities,
                    "signal": {
                        "activeLane": sig_lane,
                        "signalState": sig_state,
                        "greenTime": sig_green_time,
                        "remainingTime": sig_rem_time
                    },
                    "metrics": {
                        "latency": inf_time_ms,
                        "fps": fps_display,
                        "memory": mem_usage_mb,
                        "cpu": cpu_usage
                    }
                }
                # Dispatch background API post
                post_telemetry_to_backend(backend_url, payload)

            # Save report history (for CSV export option)
            if export_csv:
                for lane in ["A", "B", "C", "D"]:
                    count = lane_counts.get(lane, 0)
                    dens = classify_density(count)
                    status = "RED"
                    assigned_green = 0
                    if lane == sig_lane:
                        status = sig_state
                        assigned_green = sig_green_time

                    signal_history.append({
                        "timestamp": timestamp_sec,
                        "lane": lane,
                        "count": count,
                        "density": dens,
                        "assigned_green_time": assigned_green,
                        "status": status,
                    })

            # Render overlay visualizations
            lane_detector.draw_lanes(frame)
            from lane_detection.detect_lanes import draw_vehicle_tags_with_lanes
            draw_vehicle_tags_with_lanes(frame, tracks)
            draw_signal_hud(frame, lane_counts, signal_controller, fps_display, inf_time_ms)

            # Write annotated video frame
            if out_writer:
                out_writer.write(frame)

            # Display GUI window
            if show:
                cv2.imshow("Smart Traffic - Main Orchestrated Pipeline", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    logger.info("User closed window preview.")
                    break

    except KeyboardInterrupt:
        logger.warning("Process halted by keyboard interrupt.")
    except Exception as e:
        logger.error(f"Pipeline error: {e}")
    finally:
        cap.release()
        if out_writer:
            out_writer.release()
        if show:
            cv2.destroyAllWindows()

    total_time = time.time() - start_time
    avg_fps = frame_count / total_time if total_time > 0 else 0
    avg_inf = total_inf_time / frame_count if frame_count > 0 else 0

    logger.info("Pipeline Complete.")
    logger.info(f"Processed: {frame_count} frames | Avg FPS: {avg_fps:.1f} | Avg Latency: {avg_inf:.1f} ms")

    # Export report CSV if requested
    if export_csv and signal_history:
        video_name = "live_camera" if isinstance(video_source, int) else Path(video_path).stem
        csv_filename = OUTPUT_DIR / f"{video_name}_signal_logs.csv"
        export_signal_history_to_csv(signal_history, str(csv_filename))

    return True


def main():
    parser = argparse.ArgumentParser(description="Main Integrated Traffic Management Pipeline")
    parser.add_argument("--video", required=True, help="Video path or camera index")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Path to YOLO weights")
    parser.add_argument("--backend", default=os.getenv("BACKEND_URL", "http://localhost:5000"), help="Backend URL")
    parser.add_argument("--show", action="store_true", help="Display visual window GUI preview")
    parser.add_argument("--save", action="store_true", help="Save final annotated video")
    parser.add_argument("--export-csv", action="store_true", help="Export logs to CSV files")
    parser.add_argument("--post-interval", type=int, default=15, help="REST update frequency in frames")
    args = parser.parse_args()

    run_pipeline(
        video_path=args.video,
        model_path=args.model,
        backend_url=args.backend,
        show=args.show,
        save=args.save,
        export_csv=args.export_csv,
        post_interval_frames=args.post_interval
    )


if __name__ == "__main__":
    main()
