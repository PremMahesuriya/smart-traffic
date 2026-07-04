# Smart Traffic Management System

An AI-powered traffic management platform that detects vehicles, calculates lane density, adapts signal timing, prioritizes emergency vehicles, detects accidents, and predicts traffic patterns — with a real-time React dashboard.

## Tech Stack

| Layer | Technologies |
|-------|-------------|
| AI / CV | Python, OpenCV, YOLO, scikit-learn |
| Backend | Node.js, Express, JWT |
| Frontend | React, Chart.js |
| Database | MongoDB |
| DevOps | Docker, Git |

## Project Structure

```
smart-traffic-management/
├── frontend/          React dashboard
├── backend/           Node.js + Express REST API
├── ai/
│   ├── vehicle_detection/
│   ├── lane_detection/
│   ├── accident_detection/
│   └── traffic_prediction/
├── database/          Schemas & seed scripts
├── datasets/          Training / test videos
├── docs/              Requirements & architecture
├── docker/            Container configs
└── README.md
```

## Roadmap

| Phase | Duration | Focus |
|-------|----------|-------|
| 0 | 1 week | Prerequisites (Python, OpenCV, React, Node, MongoDB) |
| 1 | 1 week | Problem research → requirements document |
| 2 | 2–3 weeks | Vehicle detection & counting |
| 3 | 1 week | Lane detection & per-lane counts |
| 4 | 1 week | Traffic density calculation |
| 5 | 2 weeks | Adaptive signal algorithm |
| 6 | 2 weeks | Emergency vehicle detection |
| 7 | 2 weeks | Accident detection & alerts |
| 8 | 2 weeks | Traffic prediction (ML models) |
| 9 | 2 weeks | Backend REST APIs |
| 10 | 1 week | MongoDB collections |
| 11 | 3 weeks | React dashboard |
| 12 | Optional | Maps integration |
| 13 | — | JWT authentication & RBAC |
| 14 | — | Email / SMS / push notifications |
| 15 | — | Docker deployment |

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- MongoDB 6+
- Docker (optional)

### AI Module

```bash
cd ai
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
python vehicle_detection/detect.py --video ../datasets/sample_traffic.mp4
```

### Backend

```bash
cd backend
npm install
cp .env.example .env
npm run dev
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Docker (all services)

```bash
docker compose -f docker/docker-compose.yml up --build
```

## API Endpoints

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/api/traffic` | Current traffic data |
| GET | `/api/camera` | Camera feeds & status |
| GET | `/api/signals` | Signal states |
| POST | `/api/signal` | Update signal timing |
| GET | `/api/analytics` | Historical analytics |

## Skills Demonstrated

Python · OpenCV · AI/ML · Computer Vision · React · Node.js · Express · MongoDB · REST API · Docker · Git · System Design · Real-time Data Processing
