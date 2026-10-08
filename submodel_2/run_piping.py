"""Run piping for the current hydraulic scenarios; show results without exports."""

from dataclasses import replace

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from submodel_1.Flood_scenario_table_Dikes_16_and_43 import build_scenario_table
from submodel_2.piping import (
    calculate_piping_probability,
    calculate_piping_series,
    sample_critical_heads,
)
from submodel_2.piping_input_data import (
    DIKE_16_PARAMETERS,
    DIKE_43_PARAMETERS,
    LONGER_SEEPAGE_LENGTHS,
    RANDOM_SEEDS,
    SAMPLE_SIZE,
)


def run_piping_model(show_plots=True):
    """Return baseline, sensitivity and convergence tables for Variable Explorer."""
    hydraulic_scenarios = build_scenario_table()
    tables, sensitivity_rows, verification_rows = [], [], []
    figure, axes = (plt.subplots(2, 1, figsize=(8, 7), constrained_layout=True)
                    if show_plots else (None, [None, None]))

    for axis, (ring, parameters) in zip(axes, (
        (16, DIKE_16_PARAMETERS), (43, DIKE_43_PARAMETERS)
    )):
        levels = hydraulic_scenarios[f"Dike {ring} water level [m NAP]"].to_numpy()
        seed = RANDOM_SEEDS[ring]
        result = calculate_piping_series(levels, parameters, SAMPLE_SIZE, seed)
        tables.append(pd.DataFrame({
            "Dike ring": ring,
            "Scenario": hydraulic_scenarios["Scenario"],
            "Water level [m NAP]": levels,
            "Scenario probability [-]": hydraulic_scenarios["Scenario probability [-]"],
            "Piping MC (formal) [-]": result["monte_carlo_probabilities"],
            "Piping exact (formal) [-]": result["exact_probabilities"],
            "Piping adopted [-]": result["piping_probabilities"],
            "Above crest": result["above_crest"],
        }))
        grid = np.linspace(min(levels), parameters.crest_height_nap, 401)
        if axis is not None:
            curve = calculate_piping_series(grid, parameters, SAMPLE_SIZE, seed)
            axis.plot(grid, curve["monte_carlo_probabilities"], color="tab:orange")
            axis.set(title=f"Dike ring {ring}: piping", xlabel="River-water level [m NAP]",
                     ylabel="Conditional probability [-]", ylim=(-0.02, 1.02))
            axis.grid(alpha=0.3)

        cases = (
            ("Baseline", parameters),
            ("Longer path", replace(parameters, seepage_length=LONGER_SEEPAGE_LENGTHS[ring])),
            ("No cover credit", replace(parameters, cover_thickness=0.0)),
        )
        for case, inputs in cases:
            # Same seed gives the same C samples for each geometry alternative.
            sensitivity = calculate_piping_series(levels, inputs, SAMPLE_SIZE, seed)
            for scenario, H, exact, mc, adopted in zip(
                hydraulic_scenarios["Scenario"], levels,
                sensitivity["exact_probabilities"], sensitivity["monte_carlo_probabilities"],
                sensitivity["piping_probabilities"],
            ):
                sensitivity_rows.append([ring, case, scenario, H, exact, mc, adopted])
            critical_heads = sample_critical_heads(inputs, SAMPLE_SIZE, seed)
            endpoints = [inputs.exit_head_nap + inputs.seepage_length / coefficient
                         + inputs.cover_factor * inputs.cover_thickness
                         for coefficient in (inputs.coefficient_max, inputs.coefficient_min)]
            check_grid = np.unique(np.append(grid, [h for h in endpoints
                                                   if min(grid) <= h <= max(grid)]))
            exact = calculate_piping_probability(check_grid, inputs)
            for n in (1000, 10000, 50000, SAMPLE_SIZE):
                estimate = np.searchsorted(np.sort(critical_heads[:n]), check_grid,
                                           side="right") / n
                verification_rows.append([ring, case, n, np.max(np.abs(estimate - exact))])

    results = pd.concat(tables, ignore_index=True)
    sensitivity = pd.DataFrame(sensitivity_rows, columns=[
        "Dike ring", "Case", "Scenario", "Water level [m NAP]",
        "Piping exact (formal) [-]", "Piping MC (formal) [-]", "Piping adopted [-]",
    ])
    verification = pd.DataFrame(verification_rows, columns=[
        "Dike ring", "Case", "Samples", "Maximum absolute error",
    ])
    if show_plots:
        plt.show()
    return results, sensitivity, verification


if __name__ == "__main__":
    results, sensitivity, verification = run_piping_model()
    print(results.to_string(index=False, float_format="%.6f"))
    largest_error = verification.loc[
        verification["Samples"] == SAMPLE_SIZE, "Maximum absolute error"
    ].max()
    print(f"\nMaximum Monte Carlo error: {largest_error:.6f}")
    print("Probabilities are conditional Bligh-criterion exceedance, not annual breach risk.")
    print("NaN means above-crest: no adopted piping probability for that scenario.")
