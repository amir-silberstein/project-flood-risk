from scipy.optimize import fsolve
from numpy.typing import NDArray
import numpy as np

from hydrological.hydrological_settings import (
    DIKE43_RIVER_BED_NAP,
    DIKE43_FLOODPLAINS_BED_NAP,
    DIKE43_MAIN_CHANNEL_WIDTH,
    DIKE43_FLOODPLAINS_WIDTH,
    DIKE43_DISCHARGE_FRACTION,
)

RIVER_SLOPE: float = 0.00016

FLOODPLAINS_THRESHOLD: float = (
    DIKE43_FLOODPLAINS_BED_NAP - DIKE43_RIVER_BED_NAP
)


def calculate_water_level(
    discharge_lobith: float,
    manning_main_channel: float,
    manning_floodplains: float,
) -> float:
    """Calculate water level in m NAP for a given discharge at Lobith."""

    discharge: float = discharge_lobith * DIKE43_DISCHARGE_FRACTION

    water_depth_guess: float = (
        discharge
        / (
            DIKE43_MAIN_CHANNEL_WIDTH
            * (RIVER_SLOPE**0.5 / manning_main_channel)
        )
    ) ** (3 / 5)

    water_depth_guess = round(water_depth_guess, 2)

    if water_depth_guess <= FLOODPLAINS_THRESHOLD:
        water_depth: float = water_depth_guess

    else:

        def discharge_balance(water_depth: float) -> float:
            main_channel_depth: float = water_depth
            floodplains_depth: float = (
                water_depth - FLOODPLAINS_THRESHOLD
            )

            main_channel_area: float = (
                DIKE43_MAIN_CHANNEL_WIDTH * main_channel_depth
            )
            floodplains_area: float = (
                DIKE43_FLOODPLAINS_WIDTH * floodplains_depth
            )

            main_channel_velocity: float = (
                main_channel_depth ** (2 / 3)
                * RIVER_SLOPE**0.5
                / manning_main_channel
            )
            floodplains_velocity: float = (
                floodplains_depth ** (2 / 3)
                * RIVER_SLOPE**0.5
                / manning_floodplains
            )

            calculated_discharge: float = (
                main_channel_area * main_channel_velocity
                + floodplains_area * floodplains_velocity
            )

            return calculated_discharge - discharge

        solution: NDArray[np.float64] = fsolve(
            discharge_balance,
            water_depth_guess,
        )
        water_depth = round(float(solution[0]), 2)

    return round(water_depth + DIKE43_RIVER_BED_NAP, 2)