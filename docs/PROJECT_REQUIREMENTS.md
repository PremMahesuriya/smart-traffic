# Smart Traffic Management System — Requirements Document

> **Phase 1 deliverable.** Fill in each section as you complete problem research.

## 1. Problem Statement

Traditional fixed-time traffic signals cause unnecessary wait times during low traffic and congestion during peak hours. This system uses computer vision and adaptive algorithms to optimize signal timing in real time.

## 2. Goals

- [x] Accurate vehicle detection and classification (car, bus, truck, bike)
- [x] Per-lane vehicle counting
- [x] Traffic density classification (Low / Medium / High / Very High)
- [x] Dynamic green-light duration based on queue length
- [ ] Emergency vehicle priority (ambulance, fire truck, police)
- [ ] Accident detection with automated alerts
- [ ] Short-term traffic prediction (10 min, 30 min, 1 hour)
- [x] Real-time dashboard for operators and admins

## 3. Functional Requirements

### 3.1 Vehicle Detection (Phase 2)

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-2.1 | Read video stream from file or camera | Must |
| FR-2.2 | Detect vehicles with bounding boxes | Must |
| FR-2.3 | Classify: car, bus, truck, bike | Must |
| FR-2.4 | Output per-class counts | Must |

**Expected output example:**
```
Cars: 18
Bus: 2
Truck: 4
Bike: 21
```

### 3.2 Lane Detection (Phase 3)

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-3.1 | Detect up to 4 lanes (A–D) | Must |
| FR-3.2 | Count vehicles per lane | Must |

### 3.3 Density Calculation (Phase 4)

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-4.1 | Density = Vehicles / Lane Length | Must |
| FR-4.2 | Classify: Low, Medium, High, Very High | Must |

### 3.4 Adaptive Signals (Phase 5)

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-5.1 | Green time proportional to vehicle count | Must |
| FR-5.2 | Min/max green time bounds | Must |

**Example:**
| Lane | Vehicles | Green Time |
|------|----------|------------|
| A | 50 | 60 sec |
| B | 8 | 15 sec |

### 3.5 Emergency Priority (Phase 6)

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-6.1 | Detect ambulance, fire truck, police | Must |
| FR-6.2 | Immediate green for emergency lane | Must |
| FR-6.3 | Restore previous timer after passage | Must |

### 3.6 Accident Detection (Phase 7)

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-7.1 | Detect sudden stop / collision | Must |
| FR-7.2 | Detect vehicle blocking road | Should |
| FR-7.3 | Send alert to dashboard & notifications | Must |

### 3.7 Traffic Prediction (Phase 8)

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-8.1 | Collect time, vehicle count, weather, day, holiday | Must |
| FR-8.2 | Predict traffic at 10 / 30 / 60 min horizons | Must |

## 4. Non-Functional Requirements

| ID | Requirement |
|----|-------------|
| NFR-1 | Detection latency < 500 ms per frame (GPU) |
| NFR-2 | API response time < 200 ms |
| NFR-3 | Dashboard updates every 5 seconds |
| NFR-4 | 99% uptime for backend services |
| NFR-5 | Role-based access (admin, operator) |

## 5. System Architecture

```
Camera Feed → AI Pipeline → Backend API → MongoDB
                              ↓
                         React Dashboard
```

## 6. MongoDB Collections

| Collection | Purpose |
|------------|---------|
| users | Admin & operator accounts |
| cameras | Camera metadata & status |
| vehicles | Detection records |
| signals | Signal state & timing |
| traffic_logs | Historical density data |
| accidents | Accident reports |
| analytics | Aggregated metrics |

## 7. Research Notes

### Traditional Traffic Lights
<!-- Document how fixed-cycle signals work and their limitations -->

### Intelligent Transportation Systems (ITS)
<!-- Key findings from ITS literature -->

### Computer Vision in Traffic Monitoring
Using deep learning detectors like YOLOv8 (specifically yolov8n for edge computing) paired with persistent tracking frameworks like ByteTrack or BoT-SORT allows for the continuous monitoring of vehicles. By tracking individual vehicle centroids and evaluating their coordinates against a counting line, we establish unique crossing logs and eliminate double counting.

### Adaptive Traffic Control
<!-- Algorithms: SCATS, SCOOT, etc. -->

## 8. Open Questions

- [x] Which YOLO version / model size for edge deployment?
  - *Recommendation:* YOLOv8n (nano) or YOLOv8s (small) is ideal, offering ~3.2M parameters to run at 30+ FPS on edge units (e.g. Jetson Orin Nano, CPU servers).
- [x] Single intersection or multi-intersection support?
  - *Recommendation:* The system is designed to process individual camera channels per lane or approach, allowing easy horizontal scaling to multi-intersection coordination at the backend.
- [x] Real camera hardware or simulated feeds for demo?
  - *Recommendation:* Supported programmatically via local webcam indices, RTSP network feeds, and synthetic/simulated traffic videos.
