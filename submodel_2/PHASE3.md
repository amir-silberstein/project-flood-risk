# Phase 3: piping and combined fragility

This addition implements the requested probability combination, interpolation,
overtopping convention, L/C sensitivity, and proposed improvement screening.
It uses the available Phase-2 material and the three images supplied on
15 October 2026. The newly offered team ZIP failed to upload and was not read.
No existing repository file was changed.

## Run in Spyder

Set the working directory to the repository root. In the console:

```python
from submodel_2.run_fragility import run_fragility_model, combined_fragility
results, hydraulic_comparison, curves, sensitivity = run_fragility_model()
```

The four tables remain in Variable Explorer. Three figures show combined
mechanisms, improvement screening, and L/C sensitivity. Nothing is exported.
The old piping-only runner still works unchanged.

For console output outside Spyder:

```bash
python -m submodel_2.run_fragility
python -m pytest submodel_2/test_piping.py submodel_2/test_fragility.py -q
```

## Function for the combined fragility curve

```python
probability = combined_fragility([5.67, 6.68], ring=16)
# About [0.255329, 1.0]. Default does NOT extrapolate unknown macro tails.

trial = combined_fragility(
    [5.67, 6.68], ring=16,
    case="Crest +1 m; effective L +25 m", screening=True,
)
```

`screening=True` explicitly assumes macro probability zero below its supplied
range and constant above it. It uses a dense, piecewise-linear combined curve.
The exact crest is included and the overflow jump is handled separately; it
is not smeared across a coarse interpolation interval. `screening=False`
interpolates macro only within its supplied range and evaluates piping exactly.
If an unknown macro probability matters, the strict result is NaN. If another
mechanism is already one, the union is one regardless of the missing value.
NaN must never be replaced with zero in the integrated risk calculation.

All modelled probabilities are conditional on the same river-water level, not
annual failure probabilities. A complete physical breach process is not modelled.

## Model and source tracing

| Item | Source and use |
| --- | --- |
| Bligh progression and cover correction | `BEP_H_Cheng_UT-1.pdf`, slides 27/30; `TRSandBoilsPiping.pdf`, sec. 4.2.2, Eq. 7. Existing `piping.py` retained. |
| Uniform C | U(12,18) is a modelling assumption; lecture coefficient alternatives do not establish a distribution. |
| Geometry | Existing `piping_input_data.py`; Set 4 profiles and Vianen STIX layer boundaries. Selected hydraulic endpoints remain assumptions. |
| Macro points | Coordinate lists in supplied `result_dike_stability.tex`, plotted in submitted report Figure 5. Source values preserved exactly. |
| Five requested loads | Supplied `image(4).png`; separate from the live hydraulic outputs. |
| Combined probability | Supplied `image(6).png`: independent union of mechanisms at fixed water level. Example gives 0.676, rounded to 0.68. |
| Overtopping | `image(5).png` illustrates crest failure; existing `submodel_1/stage1_hydraulic.py` uses H > crest. Here this is a deterministic overflow/inundation trigger, not wave overtopping or certain breach. |
| Phase 3 requirements | `2026 Project Flood Risk-2.pdf`, printed p. 8: verification, uncertainty propagation, intervention and climate-change evaluation. |

For A = H - hp - 0.3d, failure is L/C <= A. If A > 0, this is C >= L/A.
For C uniform on [a,b], the fraction of that interval satisfying failure is
zero when A <= L/b, (b-L/A)/(b-a) when L/b < A < L/a, and one when A >= L/a.
This supplies the missing derivation of submitted Eq. 13. Bounded uniform C
does not yield a normal-distribution S-curve. The onset/saturation levels are
5.491/6.452 m NAP (ring 16) and 13.421/14.322 m NAP (ring 43).

The combination is P = 1 - (1-Pp)(1-Pm)(1-Po). Independence is a course
assumption, not a demonstrated physical property. Piping remains an
available-exit progression proxy. A combined value of one does not validate
certainty of physical breach. A combined curve cannot lie below any component.

## Baseline at requested heights

| Ring | H (m NAP) | Piping | Macro interpolated | Overflow | Combined |
| --- | ---: | ---: | ---: | ---: | ---: |
| 16 | 4.46 | 0 | unavailable | 0 | unavailable; screening 0 |
| 16 | 5.67 | 0.255329 | 7.14225e-9 | 0 | 0.255329 |
| 16 | 6.68 | 1 | 0.0105377 | 0 | 1 |
| 16 | 7.60 | 1 | 0.71306 | 0 | 1 |
| 16 | 8.43 | not adopted above crest | unavailable | 1 | 1 |
| 43 | 12.72 | 0 | unavailable | 0 | unavailable; screening 0 |
| 43 | 14.32 | 0.998765 | 5.2485e-7 | 0 | 0.998765 |
| 43 | 15.67 | 1 | 0.0098427 | 0 | 1 |
| 43 | 16.90 | not adopted above crest | unavailable | 1 | 1 |
| 43 | 18.02 | not adopted above crest | unavailable | 1 | 1 |

These macro probabilities are linear interpolations, not new D-Stability runs.
The ring-43 source decreases slightly between 14.50 and 14.70 m NAP; no silent
smoothing is applied. Its cross-section identity must also be confirmed because
the previously supplied STIX geometry appeared to match DD124 rather than DD123.

## Sensitivity and proposed improvement

The sensitivity figure shows P(H) for baseline L, L+10 m and L+25 m;
P(L) at the supplied 1250-year level for assumed U(12,15), U(12,18), U(15,18);
and deterministic margin g(L,C) at that level. A fixed L and C gives a margin,
not an intermediate probability. The alternative distributions are illustrative,
not inferred probabilities of soil classes. Greater L increases resistance;
greater C reduces L/C and increases failure probability in this criterion.

Four explicit screening cases are evaluated at both sites: baseline, crest +1 m,
effective L +25 m, and both changes. The candidate concept is crest raising
combined with a seepage berm/blanket; +25 m is assumed EFFECTIVE hydraulic credit,
not a justified footprint dimension. This is not an approved or optimized design.
Do not change C to improve safety without an actual justified material change.

At submitted 1250-year levels, holding macro, hp and d fixed:

| Case | Combined ring 16 | Combined ring 43 |
| --- | ---: | ---: |
| Baseline | 1 | 1 |
| Crest +1 m | 1 | 1 |
| Effective L +25 m | 0.010538 | 0.640610 |
| Crest +1 m and effective L +25 m | 0.010538 | 0.640610 |

For the extended-path case the piping components are 0 and 0.637037.
Crest raising alone cannot change piping at fixed H, L, hp and d. The original
macro response is deliberately held fixed to isolate the assumed parameter
effects; it is NOT a prediction of the redesigned slope's stability. A physical
redesign must rerun macro stability and update exit head and cover as needed.
A ditch that lowers hp or removes cover can worsen this piping criterion.
No new physical design is claimed safe by these screening results.

## Required integration changes (for the team to make)

1. Resolve the hydraulic discrepancy before using a single production run.
   The submitted table gives H1250 = 6.68/15.67 m NAP; current repository code
   gives 7.15/16.47. `hydraulic_comparison` shows all ten differences and
   `results` evaluates both separately. No teammate hydraulic file is changed.
2. In the overall runner, call `combined_fragility(H, ring)` for each selected
   hydraulic level. Decide explicitly how unknown macro tails are handled.
   Use `screening=True` only if the documented extrapolation is accepted.
3. Specify distinct failure/overflow outcome logic and initiation time before
   calling the existing breach function. Crest overflow is not automatically
   an eroded breach. Apply the appropriate unweighted discharge/hydrograph to
   the impact calculation; do not scale flow by the failure probability.
4. After conditional consequences are calculated, use
   `weighted_risk_contribution(weights, probabilities, consequences)` for EUR/year
   or expected fatalities/year when the weights are annual event-bin probabilities.
   The current weights sum to 0.08 and cover T >= 12.5 years only. Unrepresented
   lower events and within-bin variation remain to be assessed. The helper
   returns a contribution, not automatically complete annual risk. If different
   mechanisms produce different consequences, use disjoint outcome branches,
   not a single combined probability times one arbitrary consequence.
5. Rerun D-Stability for the common improved cross-section and supply the new
   macro table. Replace `MACRO_DATA` only with verified results. Additional macro
   levels are needed below 5.00/14.10 m and between the last sample and raised crest.
6. For the final Phase-3 uncertainty analysis, propagate 2-3 agreed parameters
   per model block to final risk indicators. The L/C sensitivity here is a model-
   component analysis, not a completed uncertainty analysis of overall flood risk.

No edits to Submodel 1 or 3 are needed to run these new files. Actual risk and
redesigned macro results remain unavailable; no placeholder numerical results
are substituted for them. The missing new team ZIP may contain updates.
