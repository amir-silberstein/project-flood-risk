"""Overtopping failure calculation."""

from dike_settings import DikeSettings


def calculate_overtopping_failure(
    water_level_nap: float,
    dike: DikeSettings,
) -> int:
    """Return 1 when the water level is above the dike crest, otherwise 0."""
    if water_level_nap > dike.crest_height_nap:
        return 1

    return 0
