"""Adaptive traffic signal algorithm — Phase 5."""

from shared.constants import BASE_GREEN_SEC, MAX_GREEN_SEC, MIN_GREEN_SEC


def compute_green_time(vehicle_count: int, max_vehicles: int = 60) -> int:
    """
    Priority scheduling: more vehicles → longer green time.
    Linear scaling between MIN and MAX green seconds.
    """
    if max_vehicles <= 0:
        return BASE_GREEN_SEC

    ratio = min(vehicle_count / max_vehicles, 1.0)
    green = MIN_GREEN_SEC + ratio * (MAX_GREEN_SEC - MIN_GREEN_SEC)
    return int(round(green))


def compute_signal_plan(lane_counts: dict[str, int]) -> dict[str, int]:
    """Return green-light duration (seconds) for each lane."""
    max_count = max(lane_counts.values()) if lane_counts else 1
    return {
        lane: compute_green_time(count, max_count)
        for lane, count in lane_counts.items()
    }


def print_signal_plan(plan: dict[str, int]):
    for lane, green in plan.items():
        print(f"Lane {lane}: Green = {green} sec")
