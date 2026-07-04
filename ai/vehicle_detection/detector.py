"""YOLOv8 vehicle detector wrapper."""

import logging
from ultralytics import YOLO

logger = logging.getLogger(__name__)


class VehicleDetector:
    """Wrapper class for loading and running inference with YOLOv8."""

    def __init__(self, model_path: str = "yolov8n.pt"):
        """Initialize the YOLOv8 model."""
        try:
            logger.info(f"Initializing detector with model: {model_path}")
            self.model = YOLO(model_path)
            logger.info("YOLO model loaded successfully.")
        except Exception as e:
            logger.error(f"Error loading YOLO model from '{model_path}': {e}")
            raise FileNotFoundError(f"Could not load YOLO model: {e}")

    def predict(self, frame, conf: float = 0.25, iou: float = 0.45):
        """Run standard inference (without tracking) on a single frame."""
        try:
            results = self.model(frame, conf=conf, iou=iou, verbose=False)
            return results[0]
        except Exception as e:
            logger.error(f"Inference error: {e}")
            return None
