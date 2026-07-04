"""Integration test and diagnostic verification suite for the Smart Traffic system.

Verifies AI package imports, YOLO capability, REST backend connectivity,
database storage pipelines, and health endpoint status.
"""

import sys
import os
import time

# Safeguard Windows console streams for UTF-8 compatibility
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Append AI folder to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "ai")))

# Import http request library
try:
    import requests
except ImportError:
    requests = None


def test_ai_modules():
    """Verify PyTorch, YOLOv8, and custom computer vision modular components."""
    print("Testing AI Modules...")
    try:
        from ultralytics import YOLO
        from vehicle_detection.detector import VehicleDetector
        from vehicle_detection.tracker import VehicleTracker
        from lane_detection.lane_detector import LaneDetector
        from lane_detection.lane_manager import LaneManager
        from signal_control.signal_controller import AdaptiveSignalController

        # Basic instantiation verify (dry run check)
        detector = VehicleDetector("yolov8n.pt")
        tracker = VehicleTracker(detector, "bytetrack")
        lane_detector = LaneDetector(None)
        lane_manager = LaneManager(["A", "B", "C", "D"])
        signal_controller = AdaptiveSignalController(["A", "B", "C", "D"])

        print("[PASS] AI pipeline imports and component instantiations successful.")
        return True
    except Exception as e:
        print(f"[FAIL] AI Pipeline validation failed: {e}")
        return False


def test_backend_health():
    """Verify backend server connectivity and database connection health check status."""
    print("Testing Backend API Connectivity...")
    if not requests:
        print("[FAIL] Requests module is not installed. Skip network check.")
        return False

    try:
        res = requests.get("http://localhost:5000/api/health", timeout=3)
        if res.status_code == 200:
            data = res.json()
            if data.get("status") == "ok":
                print("[PASS] Backend Express API and MongoDB database health check passed.")
                return True
            else:
                print(f"[FAIL] Backend returned degraded health state: {data}")
                return False
        else:
            print(f"[FAIL] Health check failed with HTTP status code: {res.status_code}")
            return False
    except Exception as e:
        print(f"[FAIL] Unable to connect to REST API server: {e}")
        return False


def test_internal_pipeline_posting():
    """Verify the live JSON POST API pipeline path by sending a mock frame payload."""
    print("Testing Live JSON Pipeline REST updates...")
    if not requests:
        return False

    payload = {
        "timestamp": 1.5,
        "laneCounts": {"A": 2, "B": 1, "C": 0, "D": 5},
        "densities": {"A": "Low", "B": "Low", "C": "Low", "D": "Low"},
        "signal": {
            "activeLane": "D",
            "signalState": "GREEN",
            "greenTime": 15,
            "remainingTime": 15
        },
        "metrics": {
            "latency": 33.5,
            "fps": 29.8,
            "memory": 150.0,
            "cpu": 12.5
        }
    }

    try:
        res = requests.post("http://localhost:5000/api/internal/updateTraffic", json=payload, timeout=3)
        if res.status_code == 200:
            print("[PASS] Live JSON payload insert successfully written to MongoDB.")
            return True
        else:
            print(f"[FAIL] Internal update failed with status: {res.status_code}")
            return False
    except Exception as e:
        print(f"[FAIL] Telemetry posting connection refused: {e}")
        return False


def main():
    print("==================================================")
    print("      SMART TRAFFIC SYSTEM INTEGRATION DIAGNOSTICS")
    print("==================================================")
    
    ai_status = test_ai_modules()
    print("-" * 50)
    health_status = test_backend_health()
    print("-" * 50)
    post_status = test_internal_pipeline_posting()
    print("==================================================")
    
    # Compile diagnostic scoreboard summary
    success = ai_status and health_status and post_status
    if success:
        print("DIAGNOSTIC REPORT: ALL SYSTEMS OPERATING NORMALLY [PASS]")
        sys.exit(0)
    else:
        print("DIAGNOSTIC REPORT: CRITICAL ERROR DETECTED [FAIL]")
        sys.exit(1)


if __name__ == "__main__":
    main()
