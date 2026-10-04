"""Run the stage-1 hydraulic model for both configured dike locations."""

from submodel_1.stage1_hydraulic import calculate_water_level_series
from submodel_1.stage1_input_data import (
    DIKE_16_PARAMETERS,
    DIKE_43_PARAMETERS,
    DISCHARGES_LOBITH,
    RETURN_PERIODS,
    UNCERTAINTY_BANDS,
)


def main() -> None:
    for name, parameters in (
        ("Dike 16", DIKE_16_PARAMETERS),
        ("Dike 43", DIKE_43_PARAMETERS),
    ):
        results = calculate_water_level_series(
            parameters,
            DISCHARGES_LOBITH,
            UNCERTAINTY_BANDS,
        )
        crest_height = float(results["crest_height"])
        water_levels = results["water_levels"]
        lower_levels = results["lower_levels"]
        upper_levels = results["upper_levels"]

        print(f"\n{name}")
        print(f"Dike crest height: {crest_height:.2f} m")
        print("Return period | Water level | Lower | Upper | Overtopping")
        for return_period, water_level, lower, upper in zip(
            RETURN_PERIODS,
            water_levels,
            lower_levels,
            upper_levels,
        ):
            overtopping = water_level > crest_height
            print(
                f"{return_period:>13} | {water_level:>11.2f} m | "
                f"{lower:>5.2f} m | {upper:>5.2f} m | {overtopping}"
            )


if __name__ == "__main__":
    main()
