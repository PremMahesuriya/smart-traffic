"""Per-lane vehicle tracking, counting, and CSV report logging."""

import csv
import logging
import os

logger = logging.getLogger(__name__)


class LaneManager:
    """Manages active vehicle mappings to lanes and maintains counts."""

    def __init__(self, lane_names: list[str]):
        """
        Initialize the LaneManager.

        Args:
            lane_names: List of lane names (e.g. ['A', 'B', 'C', 'D'])
        """
        self.lane_names = lane_names
        # Counts in the current frame
        self.live_counts = {name: 0 for name in lane_names}
        # Sets of unique track IDs seen in each lane to avoid duplicates
        self.cumulative_ids = {name: set() for name in lane_names}
        # List of dicts recording time-series counts per frame
        self.history = []
        logger.info(f"LaneManager initialized for lanes: {lane_names}")

    def update(self, tracks: list[dict], lane_detector, frame_idx: int, timestamp_sec: float) -> dict[str, str]:
        """
        Map each active vehicle track to its lane and update counts.

        Args:
            tracks: List of active track dicts from the tracker.
            lane_detector: Instance of LaneDetector.
            frame_idx: Current frame index.
            timestamp_sec: Current timestamp in seconds.

        Returns:
            A dict mapping track ID to lane name for the current frame.
        """
        # Reset live counts for the new frame
        self.live_counts = {name: 0 for name in self.lane_names}
        current_mappings = {}

        for track in tracks:
            bbox = track["bbox"]
            track_id = track["id"]

            # Compute centroid of bounding box
            cx = (bbox[0] + bbox[2]) / 2.0
            cy = (bbox[1] + bbox[3]) / 2.0

            # Determine lane assignment
            lane = lane_detector.get_lane_for_point((cx, cy))
            if lane:
                self.live_counts[lane] += 1
                self.cumulative_ids[lane].add(track_id)
                current_mappings[track_id] = lane
                # Store the assigned lane in the track dict for HUD rendering
                track["lane"] = lane

        # Record this frame's counts to history
        record = {
            "frame": frame_idx,
            "timestamp": timestamp_sec,
        }
        for name in self.lane_names:
            record[f"{name}_live"] = self.live_counts[name]
            record[f"{name}_cum"] = len(self.cumulative_ids[name])

        self.history.append(record)
        return current_mappings

    def get_live_counts(self) -> dict[str, int]:
        """Return the current frame's live vehicle count per lane."""
        return dict(self.live_counts)

    def get_cumulative_counts(self) -> dict[str, int]:
        """Return the total unique vehicles counted per lane."""
        return {name: len(self.cumulative_ids[name]) for name in self.lane_names}

    def export_to_csv(self, csv_path: str):
        """
        Export historical per-frame lane metrics to a CSV file.

        Args:
            csv_path: Destination CSV file path.
        """
        try:
            os.makedirs(os.path.dirname(csv_path), exist_ok=True)
            with open(csv_path, mode="w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)

                # Construct CSV headers
                headers = ["Frame", "Timestamp"]
                for name in self.lane_names:
                    headers.extend([f"Lane_{name}_Live", f"Lane_{name}_Cumulative"])
                writer.writerow(headers)

                # Write rows
                for r in self.history:
                    row = [r["frame"], f"{r['timestamp']:.2f}"]
                    for name in self.lane_names:
                        row.extend([r[f"{name}_live"], r[f"{name}_cum"]])
                    writer.writerow(row)

            logger.info(f"Successfully exported lane counting report to CSV: {csv_path}")
        except Exception as e:
            logger.error(f"Failed to export lane counts to CSV: {e}")
