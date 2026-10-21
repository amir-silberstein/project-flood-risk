import numpy as np
from dike_settings import (
    DIKE16,
    DIKE16_BERM,
    DIKE43,
    DIKE43_DRAINAGE,
    DikeSettings,
)

_DIKE16_WATER_LEVELS = np.array(
    [
        14.1, 14.3, 14.5, 14.7, 14.9, 15.1, 15.3, 15.5, 15.7,
        15.8, 15.9, 16.0, 16.1, 16.2, 16.3, 16.4, 16.54,
    ]
)
_DIKE16_PROBABILITIES = np.array(
    [
        6.8249e-8, 3.6650e-7, 1.9502e-6, 3.2197e-7, 3.5914e-6,
        3.5609e-5, 0.00030099, 0.0020382, 0.011218, 0.022128,
        0.044173, 0.082554, 0.14057, 0.22003, 0.32292, 0.43992,
        0.60807,
    ]
)
_DIKE16_BERM_PROBABILITIES = np.array(
    [
        3.3043e-34, 8.6881e-38, 7.5185e-34, 4.4418e-30, 2.6840e-26,
        3.9991e-22, 6.9298e-18, 6.5798e-15, 2.9306e-11, 9.1402e-10,
        1.5821e-8, 5.6706e-7, 6.6008e-6, 7.1387e-5, 0.00058071,
        0.0032496, 0.0252942,
    ]
)

_DIKE43_WATER_LEVELS = np.array(
    [5.0, 6.0, 6.5, 7.0, 7.08, 7.18, 7.28, 7.38, 7.48, 7.58, 7.68, 7.78, 7.88]
)
_DIKE43_PROBABILITIES = np.array(
    [
        1.54695858e-13, 1.06602445e-8, 5.35962055e-5, 0.0251736663, 0.0514562621,
        0.112699951, 0.19330924, 0.341484034, 0.516420334, 0.685766603,
        0.822101021, 0.904023508, 0.959597433,
    ]
)
_DIKE43_DRAINAGE_PROBABILITIES = np.array(
    [
        5.11187514e-17, 5.02173880e-10, 1.40997325e-5, 9.94829499e-6, 2.08332487e-5,
        5.16743069e-5, 0.000112400079, 0.000274301087, 0.000655165081, 0.00152572476,
        0.012641086, 0.0199796081, 0.0299388041,
    ]
)


def calculate_macro_stability_probability(
    water_level_nap: float,
    dike: DikeSettings,
) -> float:
    """Return the interpolated macro-stability failure probability."""

    if dike is DIKE16:
        water_levels = _DIKE16_WATER_LEVELS
        probabilities = _DIKE16_PROBABILITIES
    elif dike is DIKE16_BERM:
        water_levels = _DIKE16_WATER_LEVELS
        probabilities = _DIKE16_BERM_PROBABILITIES
    elif dike is DIKE43:
        water_levels = _DIKE43_WATER_LEVELS
        probabilities = _DIKE43_PROBABILITIES
    elif dike is DIKE43_DRAINAGE:
        water_levels = _DIKE43_WATER_LEVELS
        probabilities = _DIKE43_DRAINAGE_PROBABILITIES

    return float(np.interp(water_level_nap, water_levels, probabilities, left=0.0, right=1.0))