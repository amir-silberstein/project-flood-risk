"""Piping failure probabilities for the two dikes."""

import numpy as np

from dike_settings import DIKE16, DIKE16_WIDE, DIKE43, DIKE43_WIDE, DikeSettings
from scenario_settings import ScenarioType


_DIKE16_WATER_LEVELS = np.array(
    [5.0, 6.0, 6.5, 7.0, 7.08, 7.18, 7.28, 7.38, 7.48, 7.58, 7.68, 7.78, 7.88]
)
_DIKE16_PROBABILITIES = np.array(
    [
        1.4e-3,
        1.95e-1,
        4.841e-1,
        7.477e-1,
        7.799e-1,
        8.157e-1,
        8.47e-1,
        8.738e-1,
        8.967e-1,
        9.16e-1,
        9.32e-1,
        9.453e-1,
        9.563e-1,
    ]
)

_DIKE16_BERM_PROBABILITIES = _DIKE16_PROBABILITIES.copy()
_DIKE16_DRAINAGE_PROBABILITIES = _DIKE16_PROBABILITIES.copy()

_DIKE43_WATER_LEVELS = np.array(
    [
        14.1, 14.3, 14.5, 14.7, 14.9, 15.1, 15.3, 15.5, 15.7,
        15.8, 15.9, 16.0, 16.1, 16.2, 16.3, 16.4, 16.54,
    ]
)
_DIKE43_PROBABILITIES = np.array(
    [
        3.3e-3,
        8.7e-3,
        1.97e-2,
        3.9e-2,
        6.91e-2,
        1.114e-1,
        1.661e-1,
        2.319e-1,
        3.059e-1,
        3.45e-1,
        3.848e-1,
        4.25e-1,
        4.65e-1,
        5.045e-1,
        5.432e-1,
        5.806e-1,
        6.306e-1,
    ]
)

_DIKE43_BERM_PROBABILITIES = np.array(
    [
        1.5828e-3, 4.5925e-3, 1.12884e-2, 2.41184e-2, 4.57603e-2,
        7.84903e-2, 1.235526e-1, 1.807626e-1, 2.484677e-1, 2.854066e-1,
        3.238458e-1, 3.633336e-1, 4.03412e-1, 4.436333e-1, 4.835734e-1,
        5.228432e-1, 5.760456e-1,
    ]
)
# Placeholder until the drainage piping probabilities are available.
_DIKE43_DRAINAGE_PROBABILITIES = _DIKE43_PROBABILITIES.copy()


def calculate_piping_probability(
    water_level_nap: float,
    dike: DikeSettings,
    scenario_type: ScenarioType = ScenarioType.BASELINE,
) -> float:
    """Return the interpolated piping failure probability."""

    is_dike16 = (
        scenario_type
        in (ScenarioType.BERM_DIKE16, ScenarioType.DRAINAGE_DIKE16,
            ScenarioType.WIDE_RIVER_DIKE16)
        or dike is DIKE16
        or dike is DIKE16_WIDE
    )
    is_dike43 = (
        scenario_type
        in (ScenarioType.BERM_DIKE43, ScenarioType.DRAINAGE_DIKE43,
            ScenarioType.WIDE_RIVER_DIKE43)
        or dike is DIKE43
        or dike is DIKE43_WIDE
    )
    if is_dike16:
        water_levels = _DIKE16_WATER_LEVELS
        probabilities = (
            _DIKE16_BERM_PROBABILITIES
            if scenario_type is ScenarioType.BERM_DIKE16
            else (
                _DIKE16_DRAINAGE_PROBABILITIES
                if scenario_type is ScenarioType.DRAINAGE_DIKE16
                else _DIKE16_PROBABILITIES
            )
        )
    elif is_dike43:
        water_levels = _DIKE43_WATER_LEVELS
        probabilities = (
            _DIKE43_BERM_PROBABILITIES
            if scenario_type is ScenarioType.BERM_DIKE43
            else (
                _DIKE43_DRAINAGE_PROBABILITIES
                if scenario_type is ScenarioType.DRAINAGE_DIKE43
                else _DIKE43_PROBABILITIES
            )
        )
    else:
        raise ValueError(f"Unknown dike configuration: {dike!r}")

    return float(
        np.interp(
            water_level_nap,
            water_levels,
            probabilities,
            left=0.0,
            right=1.0,
        )
    )
