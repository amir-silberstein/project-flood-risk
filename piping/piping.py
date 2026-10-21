import numpy as np

from dike_settings import DikeSettings


def calculate_piping_probability(
    water_level_nap: float,
    dike: DikeSettings,
    sample_size: int = 200_000,
    seed: int = 20261003,
) -> float:
    """Return the Monte Carlo piping failure probability.

    Each sample draws a piping coefficient uniformly between the dike's
    configured minimum and maximum values. A sample fails when the supplied
    water level reaches its critical water level.
    """
    rng = np.random.default_rng(seed)
    coefficients = rng.uniform(
        dike.piping_coefficient_min,
        dike.piping_coefficient_max,
        sample_size,
    )

    critical_water_levels = (
        dike.exit_head_nap
        + dike.seepage_length / coefficients
        + dike.piping_cover_factor * dike.cover_thickness
    )

    return float(np.mean(critical_water_levels <= water_level_nap))
