"""Shared dike-breach simulation for the stage-1 dike models."""

from dataclasses import dataclass
import math
from typing import TypedDict


class BreachResults(TypedDict):
    times: list[float]
    breach_widths: list[float]
    breach_levels: list[float]
    downstream_depths: list[float]
    breach_discharges: list[float]
    dBdt_values: list[float]


@dataclass(frozen=True)
class BreachParameters:
    floodplain_bed_nap: float
    crest_height_nap: float
    dt: float = 10.0
    initial_width: float = 20.0
    vertical_erosion_duration: float = 600.0
    gravity: float = 10.0
    critical_velocity: float = 0.2
    erosion_factor: float = 1.2
    widening_factor: float = 0.04
    downstream_depth_ratio: float = 2 / 3
    discharge_coefficient: float = 1.0
    duration: float = 3600.0


def simulate_breach(
    water_level_nap: float,
    parameters: BreachParameters,
    *,
    t_end: float | None = None,
    print_steps: bool = False,
) -> BreachResults:
    """Simulate breach growth and discharge for one upstream water level."""
    dt = parameters.dt
    duration = parameters.duration if t_end is None else t_end
    times: list[float] = []
    breach_widths: list[float] = []
    breach_levels: list[float] = []
    downstream_depths: list[float] = []
    breach_discharges: list[float] = []
    dBdt_values: list[float] = []
    width = parameters.initial_width

    if print_steps:
        print(f"{'Time (s)':>10} | {'Breach Width B (m)':>20} | {'Discharge Q (m^3/s)':>22}")
        print("-" * 60)

    for step in range(int(duration / dt) + 1):
        time = step * dt
        if time <= parameters.vertical_erosion_duration:
            breach_level = parameters.crest_height_nap - (
                parameters.crest_height_nap - parameters.floodplain_bed_nap
            ) * (time / parameters.vertical_erosion_duration)
            width_rate = 0.0
        else:
            breach_level = parameters.floodplain_bed_nap
            upstream_depth = max(0.0, water_level_nap - breach_level)
            downstream_depth = parameters.downstream_depth_ratio * upstream_depth
            head_difference = upstream_depth - downstream_depth
            if head_difference > 0:
                horizontal_time = time - parameters.vertical_erosion_duration
                numerator = parameters.erosion_factor * parameters.widening_factor * (
                    parameters.gravity * head_difference
                ) ** 1.5
                denominator = math.log(10) * parameters.critical_velocity**2 * (
                    1
                    + parameters.widening_factor
                    * parameters.gravity
                    / parameters.critical_velocity
                    * horizontal_time
                )
                width_rate = min(numerator / denominator, 1.0)
            else:
                width_rate = 0.0

        upstream_depth = max(0.0, water_level_nap - breach_level)
        downstream_depth = (
            parameters.downstream_depth_ratio * upstream_depth
            if upstream_depth > 0
            else 0.0
        )
        discharge = (
            (2 / 3) ** 1.5
            * parameters.gravity**0.5
            * width
            * upstream_depth**1.5
            * parameters.discharge_coefficient
            if upstream_depth > 0
            else 0.0
        )

        if print_steps and step % 10 == 0:
            print(f"{time:>10.0f} | {width:>20.2f} | {discharge:>22.2f}")

        times.append(time)
        breach_widths.append(width)
        breach_levels.append(breach_level)
        downstream_depths.append(downstream_depth)
        breach_discharges.append(discharge)
        dBdt_values.append(width_rate)
        width += width_rate * dt

    return {
        "times": times,
        "breach_widths": breach_widths,
        "breach_levels": breach_levels,
        "downstream_depths": downstream_depths,
        "breach_discharges": breach_discharges,
        "dBdt_values": dBdt_values,
    }