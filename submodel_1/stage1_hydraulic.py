"""Shared hydraulic calculations for the stage-1 flood-risk model."""

from dataclasses import dataclass
from typing import Sequence

from scipy.optimize import fsolve


@dataclass(frozen=True)
class HydraulicParameters:
    """Physical and hydraulic inputs for one dike location."""

    river_bed_nap: float
    floodplain_bed_nap: float
    crest_height_nap: float
    main_channel_height: float
    discharge_fraction: float
    river_slope: float
    manning_main_channel: float
    manning_floodplain: float
    main_channel_width: float
    total_channel_width: float

    @property
    def dike_height(self) -> float:
        """Height of the dike above the floodplain."""
        return self.crest_height_nap - self.floodplain_bed_nap


def calculate_water_level(
    discharge_lobith: float,
    parameters: HydraulicParameters,
) -> tuple[float, float, bool]:
    """Calculate water level and overtopping status for a Lobith discharge."""
    discharge = discharge_lobith * parameters.discharge_fraction
    main_channel_height = parameters.main_channel_height
    main_channel_width = parameters.main_channel_width
    total_channel_width = parameters.total_channel_width
    river_slope = parameters.river_slope
    manning_main_channel = parameters.manning_main_channel
    manning_floodplain = parameters.manning_floodplain

    water_level_guess = (
        discharge
        / (main_channel_width * river_slope**0.5 / manning_main_channel)
    ) ** (3 / 5)

    if water_level_guess <= main_channel_height:
        water_level = water_level_guess
    else:
        def discharge_difference(water_level: float) -> float:
            main_area = main_channel_width * water_level
            main_velocity = (
                water_level ** (2 / 3)
                * river_slope**0.5
                / manning_main_channel
            )

            floodplain_area = (total_channel_width - main_channel_width) * (
                water_level - main_channel_height
            )
            floodplain_velocity = (
                (water_level - main_channel_height) ** (2 / 3)
                * river_slope**0.5
                / manning_floodplain
            )

            return (
                main_area * main_velocity
                + floodplain_area * floodplain_velocity
                - discharge
            )

        water_level = fsolve(discharge_difference, water_level_guess)[0]

    water_level = round(float(water_level), 2)
    water_level_nap = round(water_level + parameters.river_bed_nap, 2)
    overtopping = water_level_nap > parameters.crest_height_nap

    return water_level, water_level_nap, overtopping


def calculate_water_level_series(
    parameters: HydraulicParameters,
    discharges_lobith: Sequence[float],
    uncertainty_bands: Sequence[float] | None = None,
) -> dict[str, list[float] | float]:
    """Calculate central water levels and optional lower and upper estimates."""
    water_levels = [
        calculate_water_level(discharge, parameters)[1]
        for discharge in discharges_lobith
    ]

    result: dict[str, list[float] | float] = {
        "water_levels": water_levels,
        "crest_height": parameters.crest_height_nap,
    }

    if uncertainty_bands is not None:
        lower_levels = []
        upper_levels = []
        for discharge, band in zip(discharges_lobith, uncertainty_bands):
            lower_levels.append(
                calculate_water_level(discharge - band / 2, parameters)[1]
            )
            upper_levels.append(
                calculate_water_level(discharge + band / 2, parameters)[1]
            )

        result["lower_levels"] = lower_levels
        result["upper_levels"] = upper_levels

    return result
