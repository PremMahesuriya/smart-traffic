"""Adaptive traffic signal controller state management and priority scheduling."""

import logging
from signal_control.config import SIGNAL_TIMINGS, STARVATION_FACTOR, YELLOW_DURATION
from signal_control.density import classify_density

logger = logging.getLogger(__name__)


class AdaptiveSignalController:
    """Manages traffic light scheduling and dynamically computes green light durations."""

    def __init__(self, lane_names: list[str]):
        """Initialize the signal controller."""
        self.lane_names = lane_names
        self.current_green_lane = None
        self.pending_green_lane = None
        self.signal_state = "Red"  # Can be 'Green', 'Yellow', 'Red'
        self.timer_countdown = 0.0

        # Starvation tracking: tracks number of cycles a non-empty lane has been skipped
        self.cycles_waiting = {name: 0 for name in lane_names}
        logger.info(f"AdaptiveSignalController initialized for lanes: {lane_names}")

    def decide_next_lane(self, lane_counts: dict[str, int]) -> str | None:
        """
        Starvation-aware priority scheduler. Selects the next lane to get green.

        - Skip completely empty lanes.
        - Higher density gets priority.
        - Prevents starvation by weighting counts with skipped cycle age.
        """
        best_lane = None
        highest_score = -1.0

        for lane in self.lane_names:
            count = lane_counts.get(lane, 0)
            if count == 0:
                continue  # Skip completely empty lanes

            # Starvation priority calculation: Score = Count * (1 + Factor * CyclesWaiting)
            wait_cycles = self.cycles_waiting.get(lane, 0)
            score = count * (1.0 + STARVATION_FACTOR * wait_cycles)

            logger.info(
                f"Lane {lane} Scheduling Metrics -> Vehicles: {count} | "
                f"Wait Cycles: {wait_cycles} | Priority Score: {score:.2f}"
            )

            if score > highest_score:
                highest_score = score
                best_lane = lane

        return best_lane

    def get_green_duration(self, vehicle_count: int) -> int:
        """Compute the dynamic green light time based on vehicle density."""
        density = classify_density(vehicle_count)
        duration = SIGNAL_TIMINGS.get(density, 15)
        return duration

    def update(self, lane_counts: dict[str, int], elapsed_time_sec: float) -> dict:
        """
        Update the signal state and countdown timer.

        Args:
            lane_counts: Dict mapping lane name to current vehicle count.
            elapsed_time_sec: Time in seconds that passed since last update.

        Returns:
            Dict containing the updated signal state summary.
        """
        # Decrement the active timer countdown
        if self.timer_countdown > 0:
            self.timer_countdown = max(0.0, self.timer_countdown - elapsed_time_sec)

        # Check if the active phase timer has expired
        if self.timer_countdown <= 0:
            if self.signal_state == "Green" or self.current_green_lane is None:
                # Active green phase ended or currently idle. Choose next lane.
                next_lane = self.decide_next_lane(lane_counts)

                if next_lane is None:
                    # All lanes are empty
                    if self.current_green_lane is not None:
                        # Transition current lane through yellow to idle
                        self.signal_state = "Yellow"
                        self.pending_green_lane = None
                        self.timer_countdown = float(YELLOW_DURATION)
                        logger.info(
                            f"Signal change: Lane {self.current_green_lane} Green ended. "
                            f"No traffic detected. Transitioning to Yellow for {YELLOW_DURATION}s."
                        )
                    else:
                        # Maintain idle state
                        self.current_green_lane = None
                        self.signal_state = "Red"
                        self.timer_countdown = 1.0  # Check again in 1s
                elif next_lane == self.current_green_lane:
                    # Keep same lane green (extend timer)
                    count = lane_counts.get(next_lane, 0)
                    duration = self.get_green_duration(count)
                    self.timer_countdown = float(duration)
                    self.signal_state = "Green"
                    # Reset waiting cycles for the green lane
                    self.cycles_waiting[next_lane] = 0
                    # Increment waiting cycles for other non-empty lanes
                    for lane in self.lane_names:
                        if lane != next_lane and lane_counts.get(lane, 0) > 0:
                            self.cycles_waiting[lane] += 1
                    logger.info(
                        f"Signal update: Extending Green for Lane {next_lane} "
                        f"by {duration}s (Traffic density: {classify_density(count)})"
                    )
                else:
                    # Target lane is different. Transition current lane to yellow.
                    if self.current_green_lane is not None:
                        self.signal_state = "Yellow"
                        self.pending_green_lane = next_lane
                        self.timer_countdown = float(YELLOW_DURATION)
                        logger.info(
                            f"Signal change: Transitioning Lane {self.current_green_lane} "
                            f"to Yellow for {YELLOW_DURATION}s. Next up: Lane {next_lane}."
                        )
                    else:
                        # Immediate green (was idle)
                        self.current_green_lane = next_lane
                        self.signal_state = "Green"
                        count = lane_counts.get(next_lane, 0)
                        duration = self.get_green_duration(count)
                        self.timer_countdown = float(duration)
                        self.cycles_waiting[next_lane] = 0
                        # Increment others
                        for lane in self.lane_names:
                            if lane != next_lane and lane_counts.get(lane, 0) > 0:
                                self.cycles_waiting[lane] += 1
                        logger.info(
                            f"Signal change: Immediate Green for Lane {next_lane} "
                            f"for {duration}s (Traffic density: {classify_density(count)})"
                        )

            elif self.signal_state == "Yellow":
                # Yellow transition ended. Activate pending lane green.
                if self.pending_green_lane is not None:
                    self.current_green_lane = self.pending_green_lane
                    self.signal_state = "Green"
                    count = lane_counts.get(self.current_green_lane, 0)
                    duration = self.get_green_duration(count)
                    self.timer_countdown = float(duration)
                    # Reset wait cycles
                    self.cycles_waiting[self.current_green_lane] = 0
                    # Increment others
                    for lane in self.lane_names:
                        if lane != self.current_green_lane and lane_counts.get(lane, 0) > 0:
                            self.cycles_waiting[lane] += 1
                    logger.info(
                        f"Signal change: Lane {self.current_green_lane} is now Green "
                        f"for {duration}s (Traffic density: {classify_density(count)})"
                    )
                    self.pending_green_lane = None
                else:
                    # Empty intersection idle transition completed
                    self.current_green_lane = None
                    self.signal_state = "Red"
                    self.timer_countdown = 1.0

        return {
            "current_green_lane": self.current_green_lane,
            "signal_state": self.signal_state,
            "timer_countdown": self.timer_countdown,
            "pending_green_lane": self.pending_green_lane,
            "cycles_waiting": dict(self.cycles_waiting),
        }
