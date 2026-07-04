"""Programmatic generation of synthetic videos for evaluation."""

import os
import cv2
import numpy as np
from pathlib import Path


def generate_video(filename: str, mode: str, width: int = 640, height: int = 360, fps: int = 30, duration_frames: int = 150):
    """
    Generate a synthetic traffic video with simple 2D shapes simulating vehicles.

    Args:
        filename: Output video file path.
        mode: Theme ('day', 'night', 'webcam', 'heavy').
        width: Video frame width.
        height: Video frame height.
        fps: Video frames per second.
        duration_frames: Total frames to write.
    """
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    rel_name = f"datasets/{Path(filename).name}"
    print(f"Generating synthetic video: {rel_name} (Mode: {mode})")
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(str(filename), fourcc, fps, (width, height))

    for f in range(duration_frames):
        # 1. Background render
        if mode == "night":
            # Dark grey street background
            frame = np.ones((height, width, 3), dtype=np.uint8) * 15
            # Draw roadside trees/structures (dark green/dark grey)
            cv2.rectangle(frame, (0, 0), (80, height), (5, 15, 5), -1)
            cv2.rectangle(frame, (width - 80, 0), (width, height), (5, 15, 5), -1)
            # Draw dim yellow streetlamp spots
            for cy in [60, 180, 300]:
                cv2.circle(frame, (40, cy), 15, (50, 100, 100), -1)
                cv2.circle(frame, (width - 40, cy), 15, (50, 100, 100), -1)
            # Lane markings (dim grey)
            cv2.line(frame, (width // 2, 0), (width // 2, height), (60, 60, 60), 2)
        elif mode == "webcam":
            # High-angle overhead light grey background
            frame = np.ones((height, width, 3), dtype=np.uint8) * 160
            # Draw angled lanes (converging towards top center)
            cv2.line(frame, (width // 2 - 30, 0), (100, height), (220, 220, 220), 2)
            cv2.line(frame, (width // 2 + 30, 0), (width - 100, height), (220, 220, 220), 2)
        else:  # day or heavy
            # Light grey street background
            frame = np.ones((height, width, 3), dtype=np.uint8) * 200
            # Draw green grass on sides
            cv2.rectangle(frame, (0, 0), (80, height), (40, 180, 40), -1)
            cv2.rectangle(frame, (width - 80, 0), (width, height), (40, 180, 40), -1)
            # Lane lines (white dashed)
            cv2.line(frame, (width // 2, 0), (width // 2, height), (255, 255, 255), 2)

        # 2. Vehicle renders (boxes)
        # We draw them at positions corresponding to the mock tracker positions
        if mode == "day":
            # Vehicle 1: Car (class 2) going top to bottom in lane 1 (X: 150)
            if 10 <= f <= 110:
                y = int(10 + (f - 10) * 3.4)
                cv2.rectangle(frame, (150, y), (200, y + 40), (255, 100, 0), -1)  # Blue-ish Car
                cv2.circle(frame, (160, y + 10), 5, (50, 50, 50), -1)  # Wheels
                cv2.circle(frame, (190, y + 10), 5, (50, 50, 50), -1)
                cv2.circle(frame, (160, y + 30), 5, (50, 50, 50), -1)
                cv2.circle(frame, (190, y + 30), 5, (50, 50, 50), -1)

            # Vehicle 2: Truck (class 7) going bottom to top in lane 2 (X: 350)
            if 30 <= f <= 130:
                y = int(350 - (f - 30) * 3.2)
                cv2.rectangle(frame, (350, y), (410, y + 55), (50, 50, 240), -1)  # Red Truck cabin/bed
                cv2.rectangle(frame, (355, y + 5), (405, y + 35), (200, 200, 200), -1)

            # Vehicle 3: Motorcycle/Bike (class 3) going top to bottom in lane 3 (X: 500)
            if 55 <= f <= 145:
                y = int(10 + (f - 55) * 4.0)
                cv2.rectangle(frame, (505, y + 5), (525, y + 20), (0, 200, 200), -1)  # Yellow Bike

        elif mode == "night":
            # Vehicle 1: Car
            if 20 <= f <= 120:
                y = int(15 + (f - 20) * 3.3)
                # Draw dark silhouette + bright headlights
                cv2.rectangle(frame, (160, y), (210, y + 42), (40, 40, 40), -1)
                cv2.circle(frame, (170, y + 38), 6, (200, 255, 255), -1)  # Light beam
                cv2.circle(frame, (200, y + 38), 6, (200, 255, 255), -1)

            # Vehicle 2: Bus
            if 40 <= f <= 140:
                y = int(340 - (f - 40) * 3.2)
                # Big dark rectangle with tail lights (red)
                cv2.rectangle(frame, (380, y), (450, y + 60), (30, 30, 50), -1)
                cv2.circle(frame, (390, y + 5), 4, (50, 50, 255), -1)  # Red tail lights
                cv2.circle(frame, (440, y + 5), 4, (50, 50, 255), -1)

        elif mode == "webcam":
            # Diagonal flows
            # Vehicle 1: Car
            if 15 <= f <= 115:
                x = int(100 + (f - 15) * 2.0)
                y = int(50 + (f - 15) * 2.8)
                cv2.rectangle(frame, (x, y), (x + 45, y + 40), (120, 50, 120), -1)

            # Vehicle 2: Motorcycle
            if 45 <= f <= 135:
                x = int(450 - (f - 45) * 1.5)
                y = int(40 + (f - 45) * 3.2)
                cv2.rectangle(frame, (x, y), (x + 25, y + 25), (10, 150, 10), -1)

        elif mode == "heavy":
            # Heavy slow traffic
            # Car 1
            if 5 <= f <= 100:
                y = int(30 + (f - 5) * 2.5)
                cv2.rectangle(frame, (80, y), (125, y + 38), (150, 80, 80), -1)
            # Truck 1
            if 15 <= f <= 115:
                y = int(330 - (f - 15) * 2.2)
                cv2.rectangle(frame, (200, y), (255, y + 55), (80, 80, 150), -1)
            # Car 2
            if 25 <= f <= 125:
                y = int(20 + (f - 25) * 2.4)
                cv2.rectangle(frame, (320, y), (365, y + 38), (80, 150, 80), -1)
            # Bus 1
            if 30 <= f <= 135:
                y = int(340 - (f - 30) * 2.1)
                cv2.rectangle(frame, (420, y), (485, y + 60), (100, 100, 100), -1)
            # Bike 1
            if 50 <= f <= 145:
                y = int(10 + (f - 50) * 3.0)
                cv2.rectangle(frame, (540, y), (565, y + 25), (50, 120, 120), -1)
            # Car 3
            if 65 <= f <= 150:
                y = int(20 + (f - 65) * 2.5)
                cv2.rectangle(frame, (150, y), (195, y + 38), (180, 180, 0), -1)

        out.write(frame)

    out.release()
    print(f"Saved synthetic video: {rel_name}")


def main():
    datasets_dir = Path(__file__).resolve().parent.parent.parent / "datasets"
    os.makedirs(datasets_dir, exist_ok=True)

    generate_video(datasets_dir / "day.mp4", "day")
    generate_video(datasets_dir / "night.mp4", "night")
    generate_video(datasets_dir / "webcam.mp4", "webcam")
    generate_video(datasets_dir / "heavy_traffic.mp4", "heavy")


if __name__ == "__main__":
    main()
