"""Piping failure probabilities for the two dikes."""

import numpy as np

from dike_settings import DIKE16, DIKE43, DikeSettings


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


def calculate_piping_probability(
    water_level_nap: float,
    dike: DikeSettings,
) -> float:
    """Return the interpolated piping failure probability."""
    
    if dike is DIKE16:
        water_levels = _DIKE16_WATER_LEVELS
        probabilities = _DIKE16_PROBABILITIES
    elif dike is DIKE43:
        water_levels = _DIKE43_WATER_LEVELS
        probabilities = _DIKE43_PROBABILITIES

    return float(
        np.interp(
            water_level_nap,
            water_levels,
            probabilities,
            left=0.0,
            right=1.0,
        )
    )
