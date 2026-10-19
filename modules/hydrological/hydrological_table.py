import pandas as pd

from global_settings import RETURN_PERIODS
from dike_settings import DikeSettings
from modules.hydrological.breach import calculate_breach_discharge
from modules.hydrological.water_level import calculate_water_level


EXCEEDANCE_PROBABILITIES: list[float] = [
    1 / return_period for return_period in RETURN_PERIODS
]


def create_hydrological_table(
    Q_thresholds: list[float],
    manning_main_channel: float,
    manning_floodplains: float,
    dike: DikeSettings,
) -> pd.DataFrame:
    """Create the hydrological table for a given dike."""

    probabilities: list[float] = []
    discharges: list[float] = []
    return_periods: list[float] = []
    water_levels: list[float] = []
    breach_discharges: list[float] = []

    for i, discharge in enumerate(Q_thresholds):
        return_period: float = RETURN_PERIODS[i]

        if i < len(Q_thresholds) - 1:
            probability: float = (
                EXCEEDANCE_PROBABILITIES[i]
                - EXCEEDANCE_PROBABILITIES[i + 1]
            )
        else:
            probability = EXCEEDANCE_PROBABILITIES[i]

        water_level: float = calculate_water_level(
            discharge,
            manning_main_channel,
            manning_floodplains,
            dike,
        )

        breach_discharge: float = calculate_breach_discharge(
            water_level,
            dike,
        )

        probabilities.append(probability)
        discharges.append(discharge)
        return_periods.append(return_period)
        water_levels.append(water_level)
        breach_discharges.append(breach_discharge)

    hydrological_data: dict[str, list[float]] = {
        "return period [years]": return_periods,
        "probability": probabilities,
        "discharge [m^3/s]": discharges,
        "water level [m NAP]": water_levels,
        "breach discharge [m^3/s]": breach_discharges,
    }

    return pd.DataFrame(hydrological_data)