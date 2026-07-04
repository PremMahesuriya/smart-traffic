"""Traffic density classification logic."""

from signal_control.config import DENSITY_THRESHOLDS


def classify_density(vehicle_count: int) -> str:
    """
    Classify traffic density based on lane vehicle counts and config thresholds.

    Args:
        vehicle_count: Current number of vehicles in the lane.

    Returns:
        Density classification string ('Low', 'Medium', 'High', 'Very High')
    """
    if vehicle_count <= DENSITY_THRESHOLDS["Low"]:
        return "Low"
    elif vehicle_count <= DENSITY_THRESHOLDS["Medium"]:
        return "Medium"
    elif vehicle_count <= DENSITY_THRESHOLDS["High"]:
        return "High"
    else:
        return "Very High"
