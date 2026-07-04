"""Lane detection and per-lane vehicle counting — Phase 3."""

import argparse
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import cv2
from ultralytics import YOLO

from shared.constants import VEHICLE_CLASSES

LANE_NAMES = ["A", "B", "C", "D"]


def define_lanes(frame_width: int, frame_height: int, num_lanes: int = 4):
    """Divide the frame into vertical lane regions."""
    lane_width = frame_width // num_lanes
    lanes = {}
    for i, name in enumerate(LANE_NAMES[:num_lanes]):
        x1 = i * lane_width
        x2 = (i + 1) * lane_width if i < num_lanes - 1 else frame_width
        lanes[name] = (x1, 0, x2, frame_height)
    return lanes


def get_lane_for_point(x: float, lanes: dict) -> str | None:
    for name, (x1, _, x2, _) in lanes.items():
        if x1 <= x <= x2:
            return name
    return None


def count_by_lane(video_path: str, model_path: str = "yolov8n.pt", show: bool = False):
    model = YOLO(model_path)
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise FileNotFoundError(f"Cannot open video: {video_path}")

    lane_counts: dict[str, int] = defaultdict(int)
    lanes = None

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        h, w = frame.shape[:2]
        if lanes is None:
            lanes = define_lanes(w, h)

        results = model(frame, verbose=False)[0]

        for box in results.boxes:
            cls_id = int(box.cls[0])
            if cls_id not in VEHICLE_CLASSES:
                continue

            cx = float(box.xyxy[0][0] + box.xyxy[0][2]) / 2
            lane = get_lane_for_point(cx, lanes)
            if lane:
                lane_counts[lane] += 1

            if show and lanes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                for name, (lx1, ly1, lx2, ly2) in lanes.items():
                    cv2.line(frame, (lx2, ly1), (lx2, ly2), (255, 255, 0), 1)
                    cv2.putText(frame, f"Lane {name}", (lx1 + 5, 25),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

        if show:
            cv2.imshow("Lane Detection", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    cap.release()
    if show:
        cv2.destroyAllWindows()

    return dict(lane_counts)


def print_lane_counts(counts: dict[str, int]):
    for name in LANE_NAMES:
        print(f"Lane {name}: {counts.get(name, 0)}")


def main():
    parser = argparse.ArgumentParser(description="Lane-based vehicle counting")
    parser.add_argument("--video", required=True)
    parser.add_argument("--model", default="yolov8n.pt")
    parser.add_argument("--show", action="store_true")
    args = parser.parse_args()

    counts = count_by_lane(args.video, args.model, args.show)
    print_lane_counts(counts)


if __name__ == "__main__":
    main()
