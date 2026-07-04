"""Vehicle detection and counting — Phase 2."""

import argparse
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import cv2
from ultralytics import YOLO

from shared.constants import CLASS_DISPLAY, VEHICLE_CLASSES


def detect_vehicles(video_path: str, model_path: str = "yolov8n.pt", show: bool = False):
    """Detect and count vehicles in a video file."""
    model = YOLO(model_path)
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise FileNotFoundError(f"Cannot open video: {video_path}")

    counts: Counter = Counter()

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame, verbose=False)[0]

        for box in results.boxes:
            cls_id = int(box.cls[0])
            if cls_id not in VEHICLE_CLASSES:
                continue

            label = VEHICLE_CLASSES[cls_id]
            counts[label] += 1

            if show:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(
                    frame, label, (x1, y1 - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2,
                )

        if show:
            cv2.imshow("Vehicle Detection", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    cap.release()
    if show:
        cv2.destroyAllWindows()

    return counts


def print_counts(counts: Counter):
    """Print vehicle counts in the expected format."""
    for key in ("car", "bus", "truck", "motorcycle"):
        display = CLASS_DISPLAY.get(key, key)
        print(f"{display}: {counts.get(key, 0)}")


def main():
    parser = argparse.ArgumentParser(description="Vehicle detection from video")
    parser.add_argument("--video", required=True, help="Path to input video")
    parser.add_argument("--model", default="yolov8n.pt", help="YOLO model weights")
    parser.add_argument("--show", action="store_true", help="Show live preview")
    args = parser.parse_args()

    counts = detect_vehicles(args.video, args.model, args.show)
    print_counts(counts)


if __name__ == "__main__":
    main()
