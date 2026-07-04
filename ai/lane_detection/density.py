"""Traffic density calculation — Phase 4."""

from shared.constants import DENSITY_THRESHOLDS


def classify_density(density: float) -> str:
    if density < DENSITY_THRESHOLDS["low"]:
        return "Low"
    if density < DENSITY_THRESHOLDS["medium"]:
        return "Medium"
    if density < DENSITY_THRESHOLDS["high"]:
        return "High"
    return "Very High"


def calculate_lane_density(vehicle_count: int, lane_length_m: float) -> dict:
    """Density = Vehicles / Lane Length."""
    density = vehicle_count / lane_length_m if lane_length_m > 0 else 0.0
    return {
        "vehicle_count": vehicle_count,
        "lane_length_m": lane_length_m,
        "density": round(density, 4),
        "classification": classify_density(density),
    }


def calculate_all_lanes(lane_counts: dict[str, int], lane_length_m: float = 100.0) -> dict:
    return {
        lane: calculate_lane_density(count, lane_length_m)
        for lane, count in lane_counts.items()
    }


def print_density_report(results: dict):
    for lane, data in results.items():
        print(f"Lane {lane} → {data['classification']} (density={data['density']})")
