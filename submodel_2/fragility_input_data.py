"""Phase-3 reference data. Heights are m NAP, probabilities dimensionless."""

import numpy as np

from submodel_2.piping_input_data import DIKE_16_PARAMETERS, DIKE_43_PARAMETERS

PARAMETERS = {16: DIKE_16_PARAMETERS, 43: DIKE_43_PARAMETERS}

# Source: hydraulic scenario table supplied as image(4).png, 15 October 2026.
# Keep this separate from the live hydraulic calculation: the levels differ.
RETURN_PERIODS = np.array([12.5, 125, 1250, 12500, 125000])
DISCHARGES = np.array([9738.657, 13634.48, 17474.07, 21308.24, 25141.87])  # m3/s
SCENARIO_WEIGHTS = np.array([0.072, 0.0072, 0.00072, 0.000072, 0.000008])
SUBMITTED_LEVELS = {
    16: np.array([4.46, 5.67, 6.68, 7.60, 8.43]),
    43: np.array([12.72, 14.32, 15.67, 16.90, 18.02]),
}

# Source: result_dike_stability.tex, coordinates used in submitted Figure 5.
# These are reference-section results, NOT reruns for an improved dike.
# Preserve the small decrease at 14.50 -> 14.70 m for ring 43 for review.
MACRO_DATA = {
    16: np.array([
        [5.00, 1.547e-13], [6.00, 1.066e-8], [6.50, 0.002307],
        [7.00, 0.02517], [7.08, 0.05146], [7.18, 0.1127],
        [7.28, 0.1933], [7.38, 0.3415], [7.48, 0.5164],
        [7.58, 0.6858], [7.68, 0.8221], [7.78, 0.9040], [7.88, 0.9596],
    ]),
    43: np.array([
        [14.10, 6.825e-8], [14.30, 3.665e-7], [14.50, 1.950e-6],
        [14.70, 3.220e-7], [14.90, 3.591e-6], [15.10, 3.561e-5],
        [15.30, 0.000301], [15.50, 0.002038], [15.70, 0.01122],
        [15.80, 0.02213], [15.90, 0.04417], [16.00, 0.08255],
        [16.10, 0.1406], [16.20, 0.2200], [16.30, 0.3229],
        [16.40, 0.4399], [16.54, 0.6081],
    ]),
}

# Proposed screening changes, not measured geometry or approved designs.
# A seepage berm/blanket would have to justify the effective L increase.
# Keep hp, d and macro results fixed to isolate the effects in this model.
# A physical redesign needs geometry, groundwater and D-Stability reruns.
DESIGN_CHANGES = {
    "Baseline": (0.0, 0.0),
    "Crest +1 m": (1.0, 0.0),
    "Effective L +25 m": (0.0, 25.0),
    "Crest +1 m; effective L +25 m": (1.0, 25.0),
}  # (crest increase [m], effective seepage-length increase [m])
