# Submodel 2: piping

Run from the project root, like the other submodels:

```bash
python -m submodel_2.run_piping
```

In Spyder, set the working directory to the repository root, then run this in
its console to keep the tables in Variable Explorer:

```python
from submodel_2.run_piping import run_piping_model
results, sensitivity, verification = run_piping_model()
print(results.to_string(index=False))
```

Only piping curves are plotted. No output files are written. NumPy, pandas and
Matplotlib are already listed in the project's dependencies. The connected
hydraulic code also uses SciPy and requires Python 3.10 or newer.

## Files

- `piping_input_data.py`: site parameters and source notes.
- `piping.py`: exact and Monte Carlo calculations, using a parameter dataclass
  like the hydraulic model.
- `run_piping.py`: reads hydraulic scenarios, calculates piping and plots it.
- `test_piping.py`: numerical and integration checks.

```bash
python -m pytest submodel_2/test_piping.py
```

## Input and output

The runner calls `submodel_1.Flood_scenario_table_Dikes_16_and_43.build_scenario_table()`.
It does not execute that module's `main()` or write its CSV. Water levels in m NAP
and scenario weights come directly from that function, not the older screenshot.

`results` contains one row per dike and hydraulic scenario, with formal Monte
Carlo and analytical probabilities, the adopted Monte Carlo result and an
above-crest flag. `sensitivity` repeats the scenarios for baseline, longer path
and no-cover-credit interpretations. `verification` compares Monte Carlo with
the analytical solution at 1,000, 10,000, 50,000 and 200,000 samples.

The model uses g = L/C + 0.3*d - (H-hp) and samples C uniformly between 12 and 18.
Geometry and seeds are unchanged from the piping report. Uniformity and the
hydraulic endpoint choices are assumptions; see the input file for sources.
P = 1 means all sampled coefficients exceed the progression criterion. It does
not prove a physical breach. An available exit is assumed; uplift and heave are
not separately modelled. Above-crest adopted results are NaN, not zero.

The current hydraulic scenario code explicitly uses differences of 1/T as bin
weights, with a final tail weight, and chooses the lower discharge bound as the
representative load. These five bins total 0.08. Piping passes those weights
through without renormalising them or claiming a complete annual breach risk.

## Integration notes for the team (no teammate files changed)

No edits to Submodel 1 or 3 are needed to run this piping component. A future
combined runner can import `run_piping_model` and call it with `show_plots=False`.
For a single level, import `calculate_piping_series` and the site's parameters.
The direct `calculate_piping_probability` function returns the analytical result
and is formal above crest; use the series' `piping_probabilities` for the
above-crest exclusion.

Keep conditional failure probability separate from breach discharge. The
existing `submodel_1.breach.simulate_breach` needs a separate decision about
failure occurrence and initiation time. Do not multiply its discharge by the
piping probability before flood propagation. Scenario outcomes can be weighted
after consequence calculations once the complete event logic is agreed.

The existing impact function `submodel_3.flood.simulate_flood` takes a constant
discharge and duration. Passing a time-varying breach discharge requires either
an agreed equivalent volume/duration or an extension of that function by its
owner. This piping addition does not modify it.

Macro and piping probabilities must not simply be added: their overlap and
conditioning need an explicit combined-failure model. No macro calculations or
plots are included here.

## Report values affected by the current hydraulic code

Checked against repository commit `7378726` (the starting commit for this addition).
The current code does not reproduce the earlier supplied water-level screenshot:

| Lower-bin return period (years) | H16 (m NAP) | H43 (m NAP) | Exact piping P16 | Exact piping P43 |
| --- | --- | --- | --- | --- |
| 12.5 | 4.64 | 13.05 | 0 | 0 |
| 125 | 6.00 | 14.89 | 0.627902 | 1 |
| 1250 | 7.15 | 16.47 | 1 | 1 |
| 12500 | 8.19 | 17.89 | formal only, above crest | formal only, above crest |
| 125000 | 9.14 | 19.21 | formal only, above crest | formal only, above crest |

At the current 1250-year Vianen level, the longer-path analytical probability is
0.967537, rather than 0.660483 at the older 6.68 m NAP level. The largest checked
Monte Carlo error is now approximately 0.002741 because the grid starts at the
current hydraulic minimum, rather than the screenshot's minimum. The fragility
relation and its onset/saturation levels have not changed.

Ask the hydraulic-model owner whether the repository or the report water levels
are intended. If the repository is adopted, update sections 7.1, 7.2.2 and 8.2
of the report consistently. If the report levels are intended, the hydraulic
owner should correct their model; do not hard-code replacements into piping.
