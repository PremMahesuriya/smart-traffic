"""Configuration definitions for the vehicle detection module."""

import os
from pathlib import Path
from shared.constants import VEHICLE_CLASSES, CLASS_DISPLAY

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATASETS_DIR = BASE_DIR / "datasets"
OUTPUT_DIR = BASE_DIR / "output"

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(DATASETS_DIR, exist_ok=True)

# YOLO Defaults
DEFAULT_MODEL = "yolov8n.pt"
CONF_THRESHOLD = 0.35
IOU_THRESHOLD = 0.45
TRACKER_TYPE = "bytetrack.yaml"  # ByteTrack is faster and highly stable for static camera setups

# Counting line configuration: ((x1, y1), (x2, y2))
# If None, it will default to a horizontal line across the middle of the frame
DEFAULT_COUNTING_LINE = None  # Will be dynamically initialized based on video frame size

# Target Vehicle Class IDs (COCO format)
# 2: car, 3: motorcycle, 5: bus, 7: truck
TARGET_CLASSES = list(VEHICLE_CLASSES.keys())

# CSV Export Settings
CSV_HEADERS = ["Timestamp", "TrackID", "Class", "Direction"]
