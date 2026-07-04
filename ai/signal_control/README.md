# Phase 4 — Adaptive Traffic Signal Control & Density Classification

This module implements real-time traffic density classification and starvation-aware adaptive traffic signal control. It consumes the per-lane counts from Phase 3 and selects the active green light lane and duration dynamically.

---

## 1. Purpose
Traditional fixed-cycle traffic lights cause unnecessary wait times. This module implements a dynamic scheduling controller that prioritizes high-density approaches while guaranteeing that lower-density lanes are not starved of green time.

---

## 2. Workflow
The pipeline operates as follows on every frame:
1. **Detection & Tracking (Phases 2 & 3):** YOLOv8 detects vehicles, ByteTrack tracks persistent IDs, and the lane manager assigns them to lanes (A, B, C, D).
2. **Density Classification (Phase 4):** Vehicle counts in each lane are classified into `Low`, `Medium`, `High`, or `Very High` categories.
3. **Adaptive Controller (Phase 4):** The Priority Scheduling algorithm evaluates lanes, increments wait cycle counts, and triggers signal switches (with a 3-second Yellow transition).
4. **HUD Rendering:** Draw translucent lanes, vehicle tags, signal lights, active lanes, and green light countdown timers.
5. **Logging:** Exports log history to CSV.

---

## 3. Configuration (`config.py`)
All parameters are externalized in `config.py`:
- **Density Thresholds:**
  - `Low`: 0–5 vehicles
  - `Medium`: 6–10 vehicles
  - `High`: 11–20 vehicles
  - `Very High`: > 20 vehicles
- **Signal Timings (Green Light Durations):**
  - `Low`: 15 seconds
  - `Medium`: 25 seconds
  - `High`: 40 seconds
  - `Very High`: 60 seconds
- **Starvation Factor (`STARVATION_FACTOR`):** Controls the speed of priority aging (default `0.5`).
- **Yellow transition duration:** Default `3` seconds.

---

## 4. Scheduling Algorithm (Priority Ageing / Starvation Prevention)
To schedule signals:
1. We compute a priority score for each lane:
   $$\text{Score} = \text{VehicleCount} \times (1.0 + \text{StarvationFactor} \times \text{CyclesWaiting})$$
2. Empty lanes ($\text{VehicleCount} = 0$) are skipped (Score = 0).
3. The lane with the highest score is allocated the green light.
4. When a lane receives green, its `CyclesWaiting` is reset to 0. All other active non-empty lanes that were skipped increment their `CyclesWaiting` by 1.
5. This aging mechanism ensures that a lane with low traffic will eventually accumulate a high enough score to receive green, preventing starvation.

---

## 5. Execution

Run the CLI command from the project root:
```bash
# General execution
ai/venv/Scripts/python ai/signal_control/detect_signals.py --video datasets/day.mp4 --save --export-csv

# Live preview
ai/venv/Scripts/python ai/signal_control/detect_signals.py --video datasets/day.mp4 --show
```
