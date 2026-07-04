# Smart Traffic Frontend Dashboard

A modern, responsive React-based admin control panel for the Smart Traffic Management System.

---

## 1. Project Structure

```
frontend/src/
├── main.jsx              # App bootstrapper
├── App.jsx               # Navigation route map
├── components/           # Reusable UI widgets
│     ├── Layout.jsx      # Combines sidebar + navbar + children
│     ├── Navbar.jsx      # Top connectivity monitor
│     ├── Sidebar.jsx     # Side route selection links
│     ├── StatCard.jsx    # Metrics visual cards
│     ├── LoadingSpinner.jsx # Data load animations
│     ├── ErrorMessage.jsx   # Error banner with retry call
│     └── Footer.jsx      # Footer info
├── pages/                # High-level page views
│     ├── Home.jsx        # Dashboard overview
│     ├── LiveTraffic.jsx # Real-time per-lane statistics
│     ├── SignalMonitor.jsx # Signal states and transition tables
│     ├── TrafficAnalytics.jsx # Chart views using Recharts
│     └── SystemStatus.jsx # Database connection details
├── services/             # Axios connection libraries
│     └── api.js          # REST path mapper
└── styles/               # Design systems stylesheets
      └── global.css      # Core light-theme styles
```

---

## 2. API Integration

Integrates with the Express REST API endpoints via the Axios library client ([services/api.js](file:///c:/Users/91942/OneDrive/Ta%CC%80i%20li%C3%AA%CC%A3u/Project-1/frontend/src/services/api.js)):
- `/api/health` $\rightarrow$ System Status
- `/api/traffic/current` $\rightarrow$ Live traffic metrics
- `/api/traffic/history` $\rightarrow$ Line chart history
- `/api/traffic/analytics` $\rightarrow$ General statistics and average counts
- `/api/signals/current` $\rightarrow$ Active signal lights and timers
- `/api/signals/history` $\rightarrow$ Signal transition tables

---

## 3. How to Run

1. **Install dependencies** (Axios is already added, Recharts is in package.json):
   ```bash
   npm install
   ```

2. **Execute development server**:
   Due to Windows Execution Policies, run via CMD wrapper:
   ```bash
   cmd /c npm run dev
   ```
   Or execute directly with Node:
   ```bash
   node node_modules/vite/bin/vite.js
   ```

3. **Port**: Vite defaults to port `5173` or similar, accessible via `http://localhost:5173/` in your browser.
