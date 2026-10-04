"""Build the connected flood scenarios for Dike 16 and Dike 43."""

import pandas as pd

from .Dike16_NAP import calculate_water_level as calculate_water_level_dike16
from .Dike43_NAP import calculate_water_level as calculate_water_level_dike43

RETURN_PERIODS = (12.5, 125, 1250, 12500, 125000)
Q_THRESHOLDS = (9738.657, 13634.48, 17474.07, 21308.24, 25141.87)


def build_scenario_table() -> pd.DataFrame:
    """Calculate scenario probabilities, water levels, and overtopping flags."""
    exceedance_probabilities = [1 / period for period in RETURN_PERIODS]
    scenario_names = []
    return_period_ranges = []
    q_ranges = []
    scenario_probabilities = []
    representative_q = []

    for index in range(len(RETURN_PERIODS) - 1):
        low_period = RETURN_PERIODS[index]
        high_period = RETURN_PERIODS[index + 1]
        low_q = Q_THRESHOLDS[index]
        high_q = Q_THRESHOLDS[index + 1]
        scenario_names.append(f"Scenario {index + 1}")
        return_period_ranges.append(f"{low_period:g} <= T < {high_period:g}")
        q_ranges.append(f"{low_q:.0f} <= Q < {high_q:.0f}")
        scenario_probabilities.append(
            exceedance_probabilities[index] - exceedance_probabilities[index + 1]
        )
        representative_q.append(low_q)

    scenario_names.append(f"Scenario {len(RETURN_PERIODS)}")
    return_period_ranges.append(f"T >= {RETURN_PERIODS[-1]:g}")
    q_ranges.append(f"Q >= {Q_THRESHOLDS[-1]:.0f}")
    scenario_probabilities.append(exceedance_probabilities[-1])
    representative_q.append(Q_THRESHOLDS[-1])

    water_levels_dike16 = []
    water_levels_dike43 = []
    overtopping_dike16 = []
    overtopping_dike43 = []
    for discharge in representative_q:
        _, level_16, overtopped_16 = calculate_water_level_dike16(
            discharge, show_output=False
        )
        _, level_43, overtopped_43 = calculate_water_level_dike43(
            discharge, show_output=False
        )
        water_levels_dike16.append(level_16)
        water_levels_dike43.append(level_43)
        overtopping_dike16.append(overtopped_16)
        overtopping_dike43.append(overtopped_43)

    return pd.DataFrame(
        {
            "Scenario": scenario_names,
            "Return-period range represented": return_period_ranges,
            "Discharge range at Lobith [m3/s]": q_ranges,
            "Scenario probability [-]": scenario_probabilities,
            "Representative Q [m3/s]": representative_q,
            "Dike 16 water level [m NAP]": water_levels_dike16,
            "Dike 43 water level [m NAP]": water_levels_dike43,
            "Dike 16 overtopping": overtopping_dike16,
            "Dike 43 overtopping": overtopping_dike43,
        }
    )


def main() -> None:
    table = build_scenario_table()
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 220)
    print(
        table.to_string(
            index=False,
            formatters={
                "Scenario probability [-]": "{:.8f}".format,
                "Representative Q [m3/s]": "{:.2f}".format,
                "Dike 16 water level [m NAP]": "{:.2f}".format,
                "Dike 43 water level [m NAP]": "{:.2f}".format,
            },
        )
    )
    table.to_csv("Scenario_Probabilities.csv", index=False)


if __name__ == "__main__":
    main()
