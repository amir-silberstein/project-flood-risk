"""Combined dike failure calculation."""

import pandas as pd

from dike_settings import DikeSettings
from modules.dike.macro_stability import (
    calculate_macro_stability_probability,
)
from modules.dike.overtopping import calculate_overtopping_failure
from modules.dike.piping import calculate_piping_probability


RETURN_PERIOD_COLUMN = "return period [years]"
WATER_LEVEL_COLUMN = "water level [m NAP]"
FAILURE_PROBABILITY_COLUMN = "probability of dike failure"
MACRO_PROBABILITY_COLUMN = "probability of macro-stability failure"
PIPING_PROBABILITY_COLUMN = "probability of piping failure"
OVERTOPPING_PROBABILITY_COLUMN = "probability of overtopping failure"


def create_dike_failure_table(
    hydrological_table: pd.DataFrame,
    dike: DikeSettings,
) -> pd.DataFrame:
    """Create combined dike-failure probabilities for each return period."""

    return_periods: list[float] = []
    macro_stability_probabilities: list[float] = []
    piping_probabilities: list[float] = []
    overtopping_probabilities: list[int] = []
    failure_probabilities: list[float] = []

    for _, row in hydrological_table.iterrows():
        return_period: float = float(row[RETURN_PERIOD_COLUMN])
        water_level: float = float(row[WATER_LEVEL_COLUMN])

        macro_stability_probability: float = (
            calculate_macro_stability_probability(water_level, dike)
        )
        piping_probability: float = calculate_piping_probability(water_level, dike)
        overtopping_probability: float = calculate_overtopping_failure(
            water_level,
            dike,
        )

        failure_probability: float = 1 - (
            (1 - macro_stability_probability)
            * (1 - piping_probability)
            * (1 - overtopping_probability)
        )

        return_periods.append(return_period)
        macro_stability_probabilities.append(macro_stability_probability)
        piping_probabilities.append(piping_probability)
        overtopping_probabilities.append(overtopping_probability)
        failure_probabilities.append(failure_probability)

    return pd.DataFrame(
        {
            RETURN_PERIOD_COLUMN: return_periods,
            MACRO_PROBABILITY_COLUMN: macro_stability_probabilities,
            PIPING_PROBABILITY_COLUMN: piping_probabilities,
            OVERTOPPING_PROBABILITY_COLUMN: overtopping_probabilities,
            FAILURE_PROBABILITY_COLUMN: failure_probabilities,
        }
    )
