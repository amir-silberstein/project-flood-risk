from typing import Any

import pandas as pd

from global_settings import Q_LOBITH_BASELINE, RETURN_PERIODS
from hydrological.hydrological_settings import (
    MANNING_FLOODPLAINS,
    MANNING_MAIN_CHANNEL,
)
from hydrological.Dike16_water_level import (
    calculate_water_level as calculate_water_level_dike16,
)
from hydrological.Dike43_water_level import (
    calculate_water_level as calculate_water_level_dike43,
)


def create_hydrological_table(
    Q_thresholds: list[float],
    manning_main_channel: float,
    manning_floodplains: float,
) -> pd.DataFrame:
    """Create a hydrological table for both dikes."""

    probabilities: list[float] = []
    discharges: list[float] = []
    return_periods: list[float] = []
    water_levels_dike16: list[float] = []
    water_levels_dike43: list[float] = []

    exceedance_probabilities: list[float] = [
        1 / return_period for return_period in RETURN_PERIODS
    ]

    for i, discharge in enumerate(Q_thresholds):
        if i < len(Q_thresholds) - 1:
            probability: float = (
                exceedance_probabilities[i]
                - exceedance_probabilities[i + 1]
            )
        else:
            probability = exceedance_probabilities[i]

        probabilities.append(probability)
        discharges.append(discharge)
        return_periods.append(RETURN_PERIODS[i])

        water_levels_dike16.append(
            calculate_water_level_dike16(
                discharge,
                manning_main_channel,
                manning_floodplains,
            )
        )
        water_levels_dike43.append(
            calculate_water_level_dike43(
                discharge,
                manning_main_channel,
                manning_floodplains,
            )
        )

    hydrological_data: dict[str, list[float]] = {
        "return period [years]": return_periods,
        "probability": probabilities,
        "discharge [m^3/s]": discharges,
        "Dike 16 water level [m NAP]": water_levels_dike16,
        "Dike 43 water level [m NAP]": water_levels_dike43,
    }

    return pd.DataFrame(hydrological_data)