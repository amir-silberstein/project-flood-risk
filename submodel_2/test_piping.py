"""Checks for the piping model and the hydraulic connection."""

from dataclasses import replace

import numpy as np
import pytest

from submodel_1.Flood_scenario_table_Dikes_16_and_43 import build_scenario_table
from submodel_2.piping import calculate_piping_probability, calculate_piping_series
from submodel_2.piping_input_data import DIKE_16_PARAMETERS, DIKE_43_PARAMETERS
from submodel_2.run_piping import run_piping_model


def test_report_cases_can_still_be_reproduced():
    assert calculate_piping_probability(5.67, DIKE_16_PARAMETERS) == pytest.approx(0.2553289854)
    assert calculate_piping_probability(14.32, DIKE_43_PARAMETERS) == pytest.approx(0.9987654321)
    longer = replace(DIKE_16_PARAMETERS, seepage_length=43.67)
    assert calculate_piping_probability(6.68, longer) == pytest.approx(0.6604830830)


def test_probability_endpoints_and_monotonicity():
    for inputs in (DIKE_16_PARAMETERS, DIKE_43_PARAMETERS):
        offset = inputs.exit_head_nap + inputs.cover_factor * inputs.cover_thickness
        onset = offset + inputs.seepage_length / inputs.coefficient_max
        saturation = offset + inputs.seepage_length / inputs.coefficient_min
        assert calculate_piping_probability(onset, inputs) == pytest.approx(0, abs=1e-12)
        assert calculate_piping_probability(saturation, inputs) == pytest.approx(1)
        p = calculate_piping_probability(np.linspace(onset - 1, saturation + 1, 101), inputs)
        assert np.all(np.diff(p) >= 0)


def test_monte_carlo_agrees_with_exact_solution():
    result = calculate_piping_series(np.linspace(4.46, 7.88, 401), DIKE_16_PARAMETERS)
    error = np.max(np.abs(result['monte_carlo_probabilities'] - result['exact_probabilities']))
    # DKW simultaneous 99.9% bound for 200,000 independent samples.
    assert error < np.sqrt(np.log(2 / 0.001) / (2 * 200000))


def test_hydraulic_connection_and_no_file_exports(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    hydraulic = build_scenario_table()
    results, _, _ = run_piping_model(show_plots=False)
    for ring in (16, 43):
        subset = results[results['Dike ring'] == ring]
        np.testing.assert_array_equal(subset['Water level [m NAP]'],
                                      hydraulic[f'Dike {ring} water level [m NAP]'])
        np.testing.assert_array_equal(subset['Scenario probability [-]'],
                                      hydraulic['Scenario probability [-]'])
        assert subset.loc[subset['Above crest'], 'Piping adopted [-]'].isna().all()
    assert list(tmp_path.iterdir()) == []


def test_invalid_inputs_are_rejected():
    with pytest.raises(ValueError):
        calculate_piping_probability(np.nan, DIKE_16_PARAMETERS)
    with pytest.raises(ValueError):
        replace(DIKE_16_PARAMETERS, seepage_length=-1)
    with pytest.raises(ValueError):
        calculate_piping_series([6], DIKE_16_PARAMETERS, sample_size=0)
