"""Configuration definitions for the lane detection module."""

import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATASETS_DIR = BASE_DIR / "datasets"
OUTPUT_DIR = BASE_DIR / "output"

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Default straight lane configurations (640x360 frame)
# Represented as polygons (list of 4 coordinates)
DEFAULT_LANE_POLYGONS = {
    "A": [(0, 0), (160, 0), (160, 360), (0, 360)],
    "B": [(160, 0), (320, 0), (320, 360), (160, 360)],
    "C": [(320, 0), (480, 0), (480, 360), (320, 360)],
    "D": [(480, 0), (640, 0), (640, 360), (480, 360)],
}

# Color configurations (BGR format) for lane overlays
LANE_COLORS = {
    "A": (200, 50, 50),     # Dark Blue
    "B": (50, 200, 50),     # Dark Green
    "C": (50, 50, 200),     # Dark Red
    "D": (50, 200, 200),    # Dark Yellow
}
