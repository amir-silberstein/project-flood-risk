import numpy as np
from dike_settings import DIKE16, DIKE16_WIDE, DIKE43, DIKE43_WIDE, DikeSettings
from scenario_settings import ScenarioType

_DIKE16_WATER_LEVELS = np.array(
    [5.0, 6.0, 6.5, 7.0, 7.08, 7.18, 7.28, 7.38, 7.48, 7.58, 7.68, 7.78, 7.88]
)

_DIKE16_PROBABILITIES = np.array(
    [
        1.54695858e-13, 1.06602445e-8, 5.35962055e-5,
        2.51736663e-2, 5.14562621e-2, 1.12699951e-1,
        1.9330924e-1, 3.41484034e-1, 5.16420334e-1, 6.85766603e-1,
        8.22101021e-1, 9.04023508e-1, 9.59597433e-1,
    ]
)

_DIKE16_DRAINAGE_PROBABILITIES = np.array(
    [
        5.1118751358367174e-17,
        5.021738799707748e-10,
        1.4099732524184594e-5,
        9.948294988042985e-6,
        2.083324865019287e-5,
        5.1674306851766476e-5,
        1.1240007897827492e-4,
        2.7430108659503227e-4,
        6.551650805357848e-4,
        1.5257247624096118e-3,
        1.2641086003565283e-2,
        1.9979608075561317e-2,
        2.993880405796412e-2,
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
        6.8249e-8, 3.6650e-7, 1.9502e-6, 3.2197e-7, 3.5914e-6,
        3.5609e-5, 3.0099e-4, 2.0382e-3, 1.1218e-2, 2.2128e-2,
        4.4173e-2, 8.2554e-2, 1.4057e-1, 2.2003e-1, 3.2292e-1,
        4.3992e-1, 6.0807e-1,
    ]
)

_DIKE43_BERM_PROBABILITIES = np.array(
    [
        3.3043e-34, 8.6881e-38, 7.5185e-34, 4.4418e-30, 2.6840e-26,
        3.9991e-22, 6.9298e-18, 6.5798e-15, 2.9306e-11, 9.1402e-10,
        1.5821e-8, 5.6706e-7, 6.6008e-6, 7.1387e-5, 5.8071e-4,
        3.2496e-3, 2.52942e-2,
    ]
)


def calculate_macro_stability_probability(
    water_level_nap: float,
    dike: DikeSettings,
    scenario_type: ScenarioType = ScenarioType.BASELINE,
) -> float:
    """Return the interpolated macro-stability failure probability."""

    is_dike16 = (
        scenario_type
        in (
            ScenarioType.BERM_DIKE16,
            ScenarioType.DRAINAGE_DIKE16,
            ScenarioType.WIDE_RIVER_DIKE16,
        )
        or dike is DIKE16
        or dike is DIKE16_WIDE
    )
    is_dike43 = (
        scenario_type
        in (
            ScenarioType.BERM_DIKE43,
            ScenarioType.DRAINAGE_DIKE43,
            ScenarioType.WIDE_RIVER_DIKE43,
        )
        or dike is DIKE43
        or dike is DIKE43_WIDE
    )

    if is_dike16:
        water_levels = _DIKE16_WATER_LEVELS
        probabilities = (
            _DIKE16_DRAINAGE_PROBABILITIES
            if scenario_type is ScenarioType.DRAINAGE_DIKE16
            else _DIKE16_PROBABILITIES
        )
    elif is_dike43:
        water_levels = _DIKE43_WATER_LEVELS
        probabilities = (
            _DIKE43_BERM_PROBABILITIES
            if scenario_type in (
                ScenarioType.BERM_DIKE43,
                ScenarioType.DRAINAGE_DIKE43,
            )
            else _DIKE43_PROBABILITIES
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