"""Combine conditional mechanisms at the SAME water level (m NAP).

Independence follows the supplied course slide image(6).png. Overtopping is
a deterministic still-water crest exceedance, matching stage1_hydraulic.py.
It is an inundation trigger in this simple model, not proof of physical breach.
"""

import numpy as np

from submodel_2.piping import calculate_piping_probability


def interpolate_fragility(water_level_nap, levels_nap, probabilities,
                          extrapolation="none"):
    """Piecewise linear interpolation; never silently smooth source values.

    'none' returns NaN outside the measured/calculated range.
    'zero_hold' is an explicit SCREENING assumption: zero below the range,
    constant at the last probability above it. Neither tail is validated.
    Non-monotone source values are retained, so callers must review them.
    """
    h = np.asarray(water_level_nap, dtype=float)
    x, p = np.asarray(levels_nap, float), np.asarray(probabilities, float)
    if (x.ndim != 1 or p.shape != x.shape or x.size < 2
            or not np.all(np.isfinite(x)) or not np.all(np.diff(x) > 0)):
        raise ValueError("Provide at least two increasing, finite water levels.")
    if not np.all(np.isfinite(h)) or not np.all(np.isfinite(p)):
        raise ValueError("Interpolation inputs must be finite.")
    if np.any((p < 0) | (p > 1)):
        raise ValueError("Probabilities must lie between zero and one.")
    if extrapolation == "none":
        left, right = np.nan, np.nan
    elif extrapolation == "zero_hold":
        left, right = 0.0, p[-1]
    else:
        raise ValueError("Choose extrapolation='none' or 'zero_hold'.")
    return np.interp(h, x, p, left=left, right=right)


def combine_probabilities(piping, macro, overtopping):
    """Independent union. Unknown inputs remain NaN unless another input is 1."""
    probabilities = np.stack(np.broadcast_arrays(piping, macro, overtopping)).astype(float)
    if np.any(np.isinf(probabilities)) or np.any(
        np.isfinite(probabilities) & ((probabilities < 0) | (probabilities > 1))
    ):
        raise ValueError("Probabilities must be in [0, 1], or NaN if unavailable.")
    total = 1 - np.prod(1 - probabilities, axis=0)
    return np.where(np.any(probabilities == 1, axis=0), 1.0, total)


def calculate_combined_failure(water_level_nap, parameters, macro_data,
                               extrapolation="none"):
    """Mechanism values and combined proxy, with bounds for missing macro data.

    The strict > crest convention matches Submodel 1. The exact crest has no
    overflow in this convention. Wave overtopping and erosion are not modelled.
    Piping above crest is not adopted; overtopping supplies the combined value.
    Bounds concern missing macro probabilities, not all model uncertainty.
    """
    h = np.asarray(water_level_nap, float)
    macro_data = np.asarray(macro_data, float)
    macro = interpolate_fragility(h, macro_data[:, 0], macro_data[:, 1], extrapolation)
    overflow = (h > parameters.crest_height_nap).astype(float)
    formal_piping = calculate_piping_probability(h, parameters)
    piping = np.where(overflow == 1, np.nan, formal_piping)
    total = combine_probabilities(piping, macro, overflow)
    return {
        "piping": piping, "macro": macro, "overtopping": overflow,
        "combined": total,
        "lower_bound": combine_probabilities(piping, np.nan_to_num(macro, nan=0), overflow),
        "upper_bound": combine_probabilities(piping, np.nan_to_num(macro, nan=1), overflow),
        "macro_outside_range": (h < macro_data[0, 0]) | (h > macro_data[-1, 0]),
    }


def interpolate_combined_curve(water_level_nap, levels_nap, combined_probabilities,
                               crest_height_nap):
    """Interpolate a finite combined table BELOW crest; preserve the overflow jump.

    Include the exact crest in the supplied grid. Above crest returns 1; below
    the table returns NaN. Pass an explicitly labelled screening table if its
    macro tails were assumed. Do not bridge a missing-data gap with this call.
    """
    h = np.asarray(water_level_nap, float)
    x, p = np.asarray(levels_nap, float), np.asarray(combined_probabilities, float)
    if not np.isfinite(crest_height_nap) or x.ndim != 1 or p.shape != x.shape:
        raise ValueError("Check the crest and table dimensions.")
    if not np.all(np.isfinite(x)) or not np.all(np.diff(x) > 0):
        raise ValueError("Water levels must be finite and strictly increasing.")
    below = x <= crest_height_nap
    if not np.any(x == crest_height_nap):
        raise ValueError("The table must include the exact crest level.")
    value = interpolate_fragility(h, x[below], p[below])
    return np.where(h > crest_height_nap, 1.0, value)


def weighted_risk_contribution(scenario_weights, failure_probabilities,
                               conditional_consequences):
    """Sum w_i * P(failure|H_i) * consequence_i for the represented bins.

    Use EUR for damage (result EUR/year if weights are annual bin probabilities),
    or people for fatalities (people/year). Consequences must already be
    conditional on the specified failure/overflow outcome. This does not run
    breach or impact models and must not be used to probability-scale discharge.
    Missing bins and different failure outcomes require separate contributions.
    """
    w, p, c = [np.asarray(a, float) for a in
               (scenario_weights, failure_probabilities, conditional_consequences)]
    if w.ndim != 1 or w.size == 0 or p.shape != w.shape or c.shape != w.shape:
        raise ValueError("Provide equal, non-empty one-dimensional arrays.")
    if not all(np.all(np.isfinite(a)) for a in (w, p, c)):
        raise ValueError("Resolve unavailable probabilities/consequences before weighting.")
    if np.any(w < 0) or w.sum() > 1 + 1e-12 or np.any((p < 0) | (p > 1)) or np.any(c < 0):
        raise ValueError("Invalid probability weights or negative consequences.")
    return float(np.sum(w * p * c))
