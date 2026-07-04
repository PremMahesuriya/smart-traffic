"""Emergency vehicle detection — Phase 6."""

EMERGENCY_CLASSES = {"ambulance", "fire_truck", "police"}
EMERGENCY_KEYWORDS = ["ambulance", "fire", "police", "emergency"]
MAX_GREEN_OVERRIDE = 120


def is_emergency_label(label: str) -> bool:
    return any(kw in label.lower() for kw in EMERGENCY_KEYWORDS)


def handle_emergency(lane: str, current_plan: dict[str, int]) -> dict:
    """
    When emergency detected: immediate green for that lane.
    Returns updated plan with restoration metadata.
    """
    restored = dict(current_plan)
    restored[lane] = MAX_GREEN_OVERRIDE
    return {
        "action": "emergency_override",
        "lane": lane,
        "green_seconds": MAX_GREEN_OVERRIDE,
        "restore_plan": current_plan,
    }
