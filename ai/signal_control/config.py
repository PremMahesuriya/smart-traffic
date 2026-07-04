"""Configuration definitions for density classification and signal timing."""

import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent.parent
OUTPUT_DIR = BASE_DIR / "output"

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Density Thresholds (Maximum vehicle count to qualify for classification)
# Low       : 0-5
# Medium    : 6-10
# High      : 11-20
# Very High : > 20
DENSITY_THRESHOLDS = {
    "Low": 5,
    "Medium": 10,
    "High": 20,
    # Anything above 20 is "Very High"
}

# Signal Timings (Green light duration in seconds) per density class
SIGNAL_TIMINGS = {
    "Low": 15,
    "Medium": 25,
    "High": 40,
    "Very High": 60,
}

# Starvation Prevention Aging Coefficient
# Increase this value to elevate priority faster for waiting lanes
STARVATION_FACTOR = 0.5

# Yellow light duration (seconds) when transitioning signals
YELLOW_DURATION = 3
