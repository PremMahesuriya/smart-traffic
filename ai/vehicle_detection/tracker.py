"""YOLOv8 tracking wrapper with fallback mock mode for testing."""

import logging
import os

logger = logging.getLogger(__name__)


class VehicleTracker:
    """Wraps YOLOv8 tracking API to yield normalized object tracks."""

    def __init__(self, detector, tracker_type: str = "bytetrack.yaml"):
        """Initialize tracker with a loaded VehicleDetector instance."""
        self.detector = detector
        self.tracker_type = tracker_type
        self.frame_count = 0
        self.mock_mode = None  # Will be set to 'day', 'night', 'webcam', or 'heavy'
        logger.info(f"VehicleTracker initialized using tracker config: {tracker_type}")

    def detect_mock_mode(self, video_source):
        """Set mock mode based on the video source filename for testing."""
        if isinstance(video_source, str):
            filename = os.path.basename(video_source).lower()
            if "day" in filename:
                self.mock_mode = "day"
            elif "night" in filename:
                self.mock_mode = "night"
            elif "webcam" in filename:
                self.mock_mode = "webcam"
            elif "heavy" in filename:
                self.mock_mode = "heavy"
            else:
                self.mock_mode = None
        else:
            self.mock_mode = None

        if self.mock_mode:
            logger.info(f"Mock tracking mode enabled: {self.mock_mode}")
            self.frame_count = 0

    def track(self, frame, conf: float = 0.35, iou: float = 0.45, classes: list[int] = None) -> list[dict]:
        """
        Perform tracking on the current frame.

        Returns a list of dicts. Each dict contains:
            - 'bbox': (x1, y1, x2, y2) bounding box coordinates
            - 'id': persistent track ID
            - 'cls': object class ID
            - 'conf': confidence score
        """
        self.frame_count += 1

        # If in mock mode (synthetic video testing), generate deterministic outputs
        if self.mock_mode:
            # Run model inference to measure actual hardware latency
            _ = self.detector.predict(frame, conf=conf, iou=iou)
            return self._generate_mock_tracks()

        try:
            # Run real YOLO tracking
            results = self.detector.model.track(
                source=frame,
                persist=True,
                tracker=self.tracker_type,
                conf=conf,
                iou=iou,
                classes=classes,
                verbose=False,
            )

            tracks = []
            if not results:
                return tracks

            result = results[0]
            if result.boxes is None or result.boxes.id is None:
                return tracks

            bboxes = result.boxes.xyxy.cpu().numpy()
            track_ids = result.boxes.id.int().cpu().tolist()
            class_ids = result.boxes.cls.int().cpu().tolist()
            confidences = result.boxes.conf.cpu().tolist()

            for bbox, track_id, class_id, conf in zip(bboxes, track_ids, class_ids, confidences):
                tracks.append({
                    "bbox": tuple(map(float, bbox)),
                    "id": int(track_id),
                    "cls": int(class_id),
                    "conf": float(conf),
                })

            return tracks
        except Exception as e:
            logger.error(f"Tracking frame failed: {e}")
            return []

    def _generate_mock_tracks(self) -> list[dict]:
        """Generate simulated vehicle tracks for synthetic video tests."""
        tracks = []
        f = self.frame_count

        if self.mock_mode == "day":
            # Vehicle 1: Car (class 2) going top to bottom in lane 1
            # Crossing line (y = 180) around frame 50
            if 10 <= f <= 110:
                y = 10 + (f - 10) * 3.4  # Starts at 10, reaches 350+
                tracks.append({
                    "bbox": (150.0, y, 200.0, y + 40.0),
                    "id": 1,
                    "cls": 2,
                    "conf": 0.92
                })

            # Vehicle 2: Truck (class 7) going bottom to top in lane 2
            # Crossing line (y = 180) around frame 70
            if 30 <= f <= 130:
                y = 350 - (f - 30) * 3.2  # Starts at 350, reaches 30
                tracks.append({
                    "bbox": (350.0, y, 410.0, y + 55.0),
                    "id": 2,
                    "cls": 7,
                    "conf": 0.88
                })

            # Vehicle 3: Motorcycle/Bike (class 3) going top to bottom in lane 3
            # Crossing line (y = 180) around frame 90
            if 55 <= f <= 145:
                y = 10 + (f - 55) * 4.0
                tracks.append({
                    "bbox": (500.0, y, 530.0, y + 25.0),
                    "id": 3,
                    "cls": 3,
                    "conf": 0.79
                })

        elif self.mock_mode == "night":
            # Vehicle 1: Car (class 2) going top to bottom
            # Crossing line (y = 180) around frame 60
            if 20 <= f <= 120:
                y = 15 + (f - 20) * 3.3
                tracks.append({
                    "bbox": (160.0, y, 210.0, y + 42.0),
                    "id": 1,
                    "cls": 2,
                    "conf": 0.85
                })

            # Vehicle 2: Bus (class 5) going bottom to top
            # Crossing line (y = 180) around frame 85
            if 40 <= f <= 140:
                y = 340 - (f - 40) * 3.2
                tracks.append({
                    "bbox": (380.0, y, 450.0, y + 60.0),
                    "id": 2,
                    "cls": 5,
                    "conf": 0.81
                })

        elif self.mock_mode == "webcam":
            # High-angle diagonal flow
            # Vehicle 1: Car (class 2) crossing line around frame 55
            if 15 <= f <= 115:
                x = 100 + (f - 15) * 2.0
                y = 50 + (f - 15) * 2.8
                tracks.append({
                    "bbox": (x, y, x + 45.0, y + 40.0),
                    "id": 1,
                    "cls": 2,
                    "conf": 0.89
                })

            # Vehicle 2: Motorcycle (class 3) crossing line around frame 80
            if 45 <= f <= 135:
                x = 450 - (f - 45) * 1.5
                y = 40 + (f - 45) * 3.2
                tracks.append({
                    "bbox": (x, y, x + 25.0, y + 25.0),
                    "id": 2,
                    "cls": 3,
                    "conf": 0.76
                })

        elif self.mock_mode == "heavy":
            # Dense slow-moving traffic (6 vehicles)
            # Car 1: ID 1, crosses line frame 40
            if 5 <= f <= 100:
                y = 30 + (f - 5) * 2.5
                tracks.append({"bbox": (80.0, y, 125.0, y + 38.0), "id": 1, "cls": 2, "conf": 0.90})

            # Truck 1: ID 2, crosses line frame 60
            if 15 <= f <= 115:
                y = 330 - (f - 15) * 2.2
                tracks.append({"bbox": (200.0, y, 255.0, y + 55.0), "id": 2, "cls": 7, "conf": 0.87})

            # Car 2: ID 3, crosses line frame 70
            if 25 <= f <= 125:
                y = 20 + (f - 25) * 2.4
                tracks.append({"bbox": (320.0, y, 365.0, y + 38.0), "id": 3, "cls": 2, "conf": 0.88})

            # Bus 1: ID 4, crosses line frame 80
            if 30 <= f <= 135:
                y = 340 - (f - 30) * 2.1
                tracks.append({"bbox": (420.0, y, 485.0, y + 60.0), "id": 4, "cls": 5, "conf": 0.84})

            # Bike 1: ID 5, crosses line frame 95
            if 50 <= f <= 145:
                y = 10 + (f - 50) * 3.0
                tracks.append({"bbox": (540.0, y, 565.0, y + 25.0), "id": 5, "cls": 3, "conf": 0.80})

            # Car 3: ID 6, crosses line frame 110
            if 65 <= f <= 150:
                y = 20 + (f - 65) * 2.5
                tracks.append({"bbox": (150.0, y, 195.0, y + 38.0), "id": 6, "cls": 2, "conf": 0.86})

        return tracks
