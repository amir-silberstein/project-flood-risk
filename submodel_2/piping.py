"""Conditional piping probabilities using the corrected Bligh criterion."""

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class PipingParameters:
    """Geometry in metres; exit and crest levels in m NAP."""

    seepage_length: float
    exit_head_nap: float
    cover_thickness: float
    crest_height_nap: float
    coefficient_min: float = 12.0
    coefficient_max: float = 18.0
    cover_factor: float = 0.3

    def __post_init__(self):
        values = (self.seepage_length, self.exit_head_nap, self.cover_thickness,
                  self.crest_height_nap, self.coefficient_min,
                  self.coefficient_max, self.cover_factor)
        if not np.all(np.isfinite(values)):
            raise ValueError("Piping parameters must be finite.")
        if self.seepage_length <= 0 or self.cover_thickness < 0 or self.cover_factor < 0:
            raise ValueError("Check seepage length and cover inputs.")
        if not 0 < self.coefficient_min < self.coefficient_max:
            raise ValueError("Require 0 < coefficient_min < coefficient_max.")


def calculate_piping_probability(water_level_nap, parameters):
    """Exact P(g <= 0) for uniform C; formal only above the crest.

    g = L/C + 0.3*d - (H-hp). An available exit is assumed.
    This is criterion exceedance, not a complete physical breach probability.
    """
    levels = np.asarray(water_level_nap, dtype=float)
    if not np.all(np.isfinite(levels)):
        raise ValueError("Water levels must be finite and expressed in m NAP.")
    head = levels - parameters.exit_head_nap
    head -= parameters.cover_factor * parameters.cover_thickness
    critical_coefficient = np.full_like(head, np.inf)
    np.divide(parameters.seepage_length, head,
              out=critical_coefficient, where=head > 0)
    probability = np.clip(
        (parameters.coefficient_max - critical_coefficient)
        / (parameters.coefficient_max - parameters.coefficient_min), 0, 1
    )
    return float(probability) if probability.ndim == 0 else probability


def sample_critical_heads(parameters, sample_size=200000, seed=20261003):
    """Sample C once and calculate the head at which each sample fails."""
    if not isinstance(sample_size, (int, np.integer)) or sample_size <= 0:
        raise ValueError("Sample size must be a positive integer.")
    rng = np.random.default_rng(seed)
    coefficients = rng.uniform(parameters.coefficient_min,
                               parameters.coefficient_max, sample_size)
    return (parameters.exit_head_nap + parameters.seepage_length / coefficients
            + parameters.cover_factor * parameters.cover_thickness)


def calculate_piping_series(water_levels_nap, parameters,
                            sample_size=200000, seed=20261003):
    """Return Monte Carlo and exact probabilities at the supplied water levels.

    Above-crest formal results are retained for inspection. The adopted piping
    probabilities are NaN there because overtopping requires separate treatment.
    """
    levels = np.atleast_1d(np.asarray(water_levels_nap, dtype=float))
    if levels.ndim != 1:
        raise ValueError("Provide a one-dimensional sequence of water levels.")
    exact = calculate_piping_probability(levels, parameters)
    critical_heads = sample_critical_heads(parameters, sample_size, seed)
    monte_carlo = np.searchsorted(np.sort(critical_heads), levels,
                                 side="right") / sample_size
    above_crest = levels > parameters.crest_height_nap
    return {
        "water_levels_nap": levels,
        "monte_carlo_probabilities": monte_carlo,
        "exact_probabilities": exact,
        "piping_probabilities": np.where(above_crest, np.nan, monte_carlo),
        "above_crest": above_crest,
    }
