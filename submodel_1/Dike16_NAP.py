"""Dike 16 stage-1 model."""

from .stage1_hydraulic import calculate_water_level as _calculate
from .stage1_hydraulic import calculate_water_level_series
from .stage1_input_data import (
    DIKE_16_PARAMETERS,
    DISCHARGES_LOBITH,
    RETURN_PERIODS,
    UNCERTAINTY_BANDS,
)

RiverBedNAP = DIKE_16_PARAMETERS.river_bed_nap
FloodplainsBedNAP = DIKE_16_PARAMETERS.floodplain_bed_nap
CrestHeightNAP = DIKE_16_PARAMETERS.crest_height_nap


def calculate_water_level(discharge_Lobith: float, show_output: bool = True):
    relative_level, water_level_nap, overtopping = _calculate(
        discharge_Lobith, DIKE_16_PARAMETERS
    )
    if show_output:
        print(
            f"The water level at discharge {discharge_Lobith} m^3/s at Lobith "
            f"is {water_level_nap} m (NAP)"
        )
        if overtopping:
            print("WARNING! Water level is above the dike height. Overtopping has occurred.")
    return relative_level, water_level_nap, overtopping


def water_level_data():
    results = calculate_water_level_series(
        DIKE_16_PARAMETERS, DISCHARGES_LOBITH, UNCERTAINTY_BANDS
    )
    return (
        list(RETURN_PERIODS),
        list(DISCHARGES_LOBITH),
        results["water_levels"],
        results["lower_levels"],
        results["upper_levels"],
        results["crest_height"],
    )


def plot_water_levels(return_periods, water_levels, lower_levels, upper_levels, crest_height):
    import matplotlib.pyplot as plt

    plt.figure(figsize=(10, 6))
    plt.plot(return_periods, water_levels, marker="o", label="Water level (NAP)")
    plt.fill_between(return_periods, lower_levels, upper_levels, alpha=0.3, label="95% confidence band")
    plt.axhline(crest_height, color="red", linestyle="--", label="Dike crest level (NAP)")
    plt.xscale("log")
    plt.xticks(return_periods, return_periods)
    plt.xlabel("Return period [years]")
    plt.ylabel("Water level [m] (NAP)")
    plt.title("Water level versus return period. Dike 16")
    plt.legend(loc="upper left")
    plt.grid(True)
    plt.show()


def run_water_level_model() -> None:
    plot_water_levels(*water_level_data())


if __name__ == "__main__":
    run_water_level_model()
