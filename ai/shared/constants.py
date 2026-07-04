"""Shared constants for the AI pipeline."""

VEHICLE_CLASSES = {
    2: "car",
    3: "motorcycle",
    5: "bus",
    7: "truck",
}

# Map COCO classes to our display names
CLASS_DISPLAY = {
    "car": "Cars",
    "motorcycle": "Bike",
    "bus": "Bus",
    "truck": "Truck",
}

DENSITY_THRESHOLDS = {
    "low": 0.15,
    "medium": 0.35,
    "high": 0.55,
    # above 0.55 = very_high
}

MIN_GREEN_SEC = 15
MAX_GREEN_SEC = 90
BASE_GREEN_SEC = 30
