"""Run from the repository root: python -m submodel_2.run_fragility.

Three figures appear in Spyder/Matplotlib; no files are exported. Tables are
returned for Variable Explorer. Both hydraulic sources remain visible.
"""

from dataclasses import replace

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from submodel_1.Flood_scenario_table_Dikes_16_and_43 import build_scenario_table
from submodel_2.fragility import calculate_combined_failure, interpolate_combined_curve
from submodel_2.fragility_input_data import (
    DESIGN_CHANGES, DISCHARGES, MACRO_DATA, PARAMETERS, RETURN_PERIODS,
    SCENARIO_WEIGHTS, SUBMITTED_LEVELS,
)
from submodel_2.piping import calculate_piping_probability


def design_parameters(ring, case):
    crest_change, length_change = DESIGN_CHANGES[case]
    p = PARAMETERS[ring]
    return replace(p, crest_height_nap=p.crest_height_nap + crest_change,
                   seepage_length=p.seepage_length + length_change)


def curve_grid(ring, parameters):
    p = parameters
    onset = p.exit_head_nap + p.cover_factor * p.cover_thickness + p.seepage_length / p.coefficient_max
    saturation = p.exit_head_nap + p.cover_factor * p.cover_thickness + p.seepage_length / p.coefficient_min
    start = min(SUBMITTED_LEVELS[ring][0], onset - 0.2)
    stop = max(SUBMITTED_LEVELS[ring][-1], p.crest_height_nap + 0.5)
    return np.unique(np.r_[np.linspace(start, stop, 3001), onset, saturation,
                           MACRO_DATA[ring][:, 0], p.crest_height_nap,
                           np.nextafter(p.crest_height_nap, np.inf)])


def combined_fragility(water_level_nap, ring, case="Baseline", screening=False):
    """Callable handoff for a level or array in m NAP.

    Default: analytical piping plus interpolation of supplied macro values;
    unknown macro tails give NaN unless another mechanism is certain.
    screening=True: interpolate a dense combined curve with explicitly assumed
    zero/held macro tails. Improved cases also HOLD baseline macro values fixed.
    """
    p = design_parameters(ring, case)
    if not screening:
        return calculate_combined_failure(water_level_nap, p, MACRO_DATA[ring])["combined"]
    grid = curve_grid(ring, p)
    total = calculate_combined_failure(grid, p, MACRO_DATA[ring], "zero_hold")["combined"]
    return interpolate_combined_curve(water_level_nap, grid, total, p.crest_height_nap)


def run_fragility_model(show_plots=True):
    """Return results, hydraulic_comparison, curves, sensitivity (no exports)."""
    hydraulic = build_scenario_table()
    if not np.allclose(hydraulic["Representative Q [m3/s]"], DISCHARGES):
        raise ValueError("Hydraulic discharges changed: review scenario correspondence.")
    if not np.allclose(hydraulic["Scenario probability [-]"], SCENARIO_WEIGHTS):
        raise ValueError("Hydraulic weights changed: review scenario correspondence.")
    tables, comparison_rows, curve_tables, sensitivity_rows = [], [], [], []
    for ring, reference in PARAMETERS.items():
        live_levels = hydraulic[f"Dike {ring} water level [m NAP]"].to_numpy()
        for T, hs, hl in zip(RETURN_PERIODS, SUBMITTED_LEVELS[ring], live_levels):
            comparison_rows.append([ring, T, hs, hl, hl - hs])
        for case in DESIGN_CHANGES:
            p = design_parameters(ring, case)
            for source, levels in (("Submitted table", SUBMITTED_LEVELS[ring]),
                                   ("Repository hydro", live_levels)):
                strict = calculate_combined_failure(levels, p, MACRO_DATA[ring])
                screen = calculate_combined_failure(levels, p, MACRO_DATA[ring], "zero_hold")
                tables.append(pd.DataFrame({
                    "Source": source, "Ring": ring, "Case": case,
                    "Return period [yr]": RETURN_PERIODS, "H [m NAP]": levels,
                    "Weight [-]": SCENARIO_WEIGHTS,
                    "Crest [m NAP]": p.crest_height_nap, "L [m]": p.seepage_length,
                    "Piping [-]": strict["piping"], "Macro supplied [-]": strict["macro"],
                    "Overflow [-]": strict["overtopping"],
                    "Combined strict [-]": strict["combined"],
                    "Combined screening [-]": screen["combined"],
                    "Missing-macro lower [-]": strict["lower_bound"],
                    "Missing-macro upper [-]": strict["upper_bound"],
                    "Macro tail assumed": screen["macro_outside_range"],
                    "Redesign macro rerun missing": case != "Baseline",
                    "Macro source needs review": ring == 43,
                }))
            grid = curve_grid(ring, p)
            strict = calculate_combined_failure(grid, p, MACRO_DATA[ring])
            screen = calculate_combined_failure(grid, p, MACRO_DATA[ring], "zero_hold")
            curve_tables.append(pd.DataFrame({
                "Ring": ring, "Case": case, "H [m NAP]": grid,
                "Piping [-]": strict["piping"], "Macro screening [-]": screen["macro"],
                "Overflow [-]": strict["overtopping"],
                "Combined strict [-]": strict["combined"],
                "Combined screening [-]": screen["combined"],
                "Macro tail assumed": screen["macro_outside_range"],
            }))
        # Uniform subsets stay within the lecture's 12--18 coefficient range.
        # All three distributions are assumptions, not fitted soil statistics.
        for L in np.linspace(20, 100, 161):
            for cmin, cmax in ((12, 15), (12, 18), (15, 18)):
                p = replace(reference, seepage_length=L, coefficient_min=cmin, coefficient_max=cmax)
                H = SUBMITTED_LEVELS[ring][2]
                sensitivity_rows.append([ring, H, L, cmin, cmax, calculate_piping_probability(H, p)])

    results = pd.concat(tables, ignore_index=True)
    comparison = pd.DataFrame(comparison_rows, columns=[
        "Ring", "Return period [yr]", "Submitted H [m NAP]",
        "Repository H [m NAP]", "Difference [m]",
    ])
    curves = pd.concat(curve_tables, ignore_index=True)
    sensitivity = pd.DataFrame(sensitivity_rows, columns=[
        "Ring", "H [m NAP]", "L [m]", "C min", "C max", "Piping [-]",
    ])
    if show_plots:
        plot_results(curves, sensitivity)
        plt.show()
    return results, comparison, curves, sensitivity


def plot_results(curves, sensitivity):
    """Reference mechanisms, intervention screening, and L/C sensitivity."""
    fig1, ax1 = plt.subplots(2, 1, figsize=(9, 8), constrained_layout=True)
    fig2, ax2 = plt.subplots(2, 1, figsize=(9, 8), constrained_layout=True)
    fig3, ax3 = plt.subplots(2, 3, figsize=(15, 8), constrained_layout=True)
    for row, (ring, reference) in enumerate(PARAMETERS.items()):
        baseline = curves[(curves.Ring == ring) & (curves.Case == "Baseline")]
        h = baseline["H [m NAP]"]
        a = ax1[row]
        for name, color, style in (("Piping [-]", "tab:orange", "--"),
                                    ("Macro screening [-]", "tab:blue", ":"),
                                    ("Overflow [-]", "tab:red", "-."),
                                    ("Combined screening [-]", "black", "-")):
            a.plot(h, baseline[name], color=color, ls=style, label=name.replace(" [-]", ""))
        a.scatter(*MACRO_DATA[ring].T, s=12, color="tab:blue", label="Supplied macro points")
        a.axvline(reference.crest_height_nap, color="grey", ls=":", label="Crest")
        a.set_title(f"Ring {ring}: reference conditional curves (assumed macro tails)")

        for case in DESIGN_CHANGES:
            table = curves[(curves.Ring == ring) & (curves.Case == case)]
            ax2[row].plot(table["H [m NAP]"], table["Combined screening [-]"], label=case)
        ax2[row].set_title(f"Ring {ring}: screening only; baseline macro curve held fixed")
        for a in (ax1[row], ax2[row]):
            a.set(xlabel="River-water level [m NAP]", ylabel="Conditional probability [-]",
                  ylim=(-0.02, 1.03))
            a.grid(alpha=0.25)
            a.legend(fontsize=8, loc="upper left")

        hs = np.linspace(SUBMITTED_LEVELS[ring][0], reference.crest_height_nap, 500)
        for delta in (0, 10, 25):
            p = replace(reference, seepage_length=reference.seepage_length + delta)
            ax3[row, 0].plot(hs, calculate_piping_probability(hs, p), label=f"L={p.seepage_length:.2f} m")
        ax3[row, 0].set(xlabel="Water level [m NAP]", ylabel="Piping probability [-]",
                        title=f"Ring {ring}: length sensitivity")
        s = sensitivity[sensitivity.Ring == ring]
        for cmin, cmax in ((12, 15), (12, 18), (15, 18)):
            part = s[(s["C min"] == cmin) & (s["C max"] == cmax)]
            ax3[row, 1].plot(part["L [m]"], part["Piping [-]"], label=f"C ~ U({cmin},{cmax})")
        H = SUBMITTED_LEVELS[ring][2]
        ax3[row, 1].set(xlabel="Effective seepage length L [m]", ylabel="Piping probability [-]",
                        title=f"H={H:.2f} m NAP; assumed distributions")
        length, coefficient = np.meshgrid(np.linspace(20, 100, 161), np.linspace(12, 18, 121))
        margin = length / coefficient + 0.3 * reference.cover_thickness - (H - reference.exit_head_nap)
        bound = np.max(np.abs(margin))
        im = ax3[row, 2].pcolormesh(length, coefficient, margin, shading="auto",
                                  cmap="RdBu", vmin=-bound, vmax=bound, rasterized=True)
        ax3[row, 2].contour(length, coefficient, margin, levels=[0], colors="black")
        ax3[row, 2].set(xlabel="Effective seepage length L [m]", ylabel="Fixed coefficient C [-]",
                        title=f"Ring {ring}: margin g (failure when g <= 0)")
        fig3.colorbar(im, ax=ax3[row, 2], label="Margin g [m]")
        for a in ax3[row, :2]:
            a.set_ylim(-0.02, 1.03)
            a.legend(fontsize=8)
            a.grid(alpha=0.25)
    return fig1, fig2, fig3


if __name__ == "__main__":
    results, hydraulic_comparison, curves, sensitivity = run_fragility_model()
    columns = ["Ring", "H [m NAP]", "Piping [-]", "Macro supplied [-]",
               "Overflow [-]", "Combined strict [-]", "Combined screening [-]", "Macro tail assumed"]
    print("BASELINE AT SUBMITTED WATER LEVELS")
    print(results[(results.Source == "Submitted table") & (results.Case == "Baseline")]
          [columns].to_string(index=False, float_format="%.6g"))
    print("\nHYDRAULIC SOURCE COMPARISON")
    print(hydraulic_comparison.to_string(index=False))
    print("\nSCREENING DESIGNS AT SUBMITTED 1250-YEAR LEVELS")
    print(results[(results.Source == "Submitted table") & (results["Return period [yr]"] == 1250)]
          [["Ring", "Case", "L [m]", "Crest [m NAP]", "Combined screening [-]"]].to_string(index=False))
    print("\nNaN = unavailable, not zero. Macro tails are assumed only in screening columns.")
    print("Ring 43 macro source is non-monotone and section identity needs confirmation.")
    print("Improvement curves hold macro stability fixed: redesigned D-Stability runs are still needed.")
    print("Weights cover only the supplied extreme-event bins (sum 0.08); no annual risk is claimed.")
