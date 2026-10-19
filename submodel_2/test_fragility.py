"""Numerical and integration checks; no new physical validation is implied."""

from dataclasses import replace

import numpy as np
import pytest

from submodel_2.fragility import (
    calculate_combined_failure, combine_probabilities,
    interpolate_combined_curve, interpolate_fragility, weighted_risk_contribution,
)
from submodel_2.fragility_input_data import MACRO_DATA, PARAMETERS, SUBMITTED_LEVELS
from submodel_2.run_fragility import combined_fragility, run_fragility_model


def test_course_slide_union_and_probability_bounds():
    assert combine_probabilities(0.4, 0.4, 0.1) == pytest.approx(0.676)
    rng = np.random.default_rng(10)
    ps = rng.uniform(0, 1, (3, 100))
    total = combine_probabilities(*ps)
    assert np.all(total >= ps.max(axis=0))
    assert np.all(total <= np.minimum(1, ps.sum(axis=0)))
    assert combine_probabilities(np.nan, 0.1, 1) == 1
    assert np.isnan(combine_probabilities(np.nan, 0.1, 0))


def test_interpolation_does_not_hide_missing_values_or_change_source_points():
    for data in MACRO_DATA.values():
        np.testing.assert_array_equal(interpolate_fragility(data[:, 0], *data.T), data[:, 1])
        assert np.isnan(interpolate_fragility(data[0, 0] - 1, *data.T))
        assert np.isnan(interpolate_fragility(data[-1, 0] + 1, *data.T))
    assert np.any(np.diff(MACRO_DATA[43][:, 1]) < 0)  # retained source issue
    with pytest.raises(ValueError):
        interpolate_fragility(2, [1, 1], [0, 1])
    with pytest.raises(ValueError):
        combine_probabilities(-0.1, 0, 0)


def test_overtopping_jump_is_not_spread_by_interpolation():
    x = np.array([1, 2, 3, 4])
    p = np.array([0, 0.1, 0.2, 1])
    h = np.array([2.999, 3, np.nextafter(3.0, np.inf), 3.5])
    answer = interpolate_combined_curve(h, x, p, 3)
    np.testing.assert_allclose(answer, [0.1999, 0.2, 1, 1])
    with pytest.raises(ValueError):
        interpolate_combined_curve(2, x, p, 3.1)


def test_higher_crest_alone_does_not_change_subcrest_piping():
    for ring, p in PARAMETERS.items():
        h = SUBMITTED_LEVELS[ring][:3]
        old = calculate_combined_failure(h, p, MACRO_DATA[ring])
        new = calculate_combined_failure(h, replace(p, crest_height_nap=p.crest_height_nap + 1), MACRO_DATA[ring])
        np.testing.assert_array_equal(old["piping"], new["piping"])
        np.testing.assert_array_equal(old["combined"], new["combined"])


def test_combined_interpolator_matches_direct_calculation():
    for ring, p in PARAMETERS.items():
        h = np.linspace(SUBMITTED_LEVELS[ring][0], p.crest_height_nap + 0.5, 987)
        exact = calculate_combined_failure(h, p, MACRO_DATA[ring], "zero_hold")["combined"]
        np.testing.assert_allclose(combined_fragility(h, ring, screening=True), exact, atol=1e-5)


def test_screening_length_improvement_and_baseline_results():
    for ring in PARAMETERS:
        h = SUBMITTED_LEVELS[ring][2]
        assert combined_fragility(h, ring) == 1
        assert combined_fragility(h, ring, "Effective L +25 m") < 1
    assert combined_fragility(5.67, 16) == pytest.approx(0.2553289907)
    assert combined_fragility(14.32, 43) == pytest.approx(0.99876543275)
    assert np.isnan(combined_fragility(4.46, 16))
    assert combined_fragility(4.46, 16, screening=True) == 0


def test_risk_weighting_uses_probabilities_not_scaled_discharge():
    assert weighted_risk_contribution([0.01, 0.001], [0.2, 1], [100, 1000]) == pytest.approx(1.2)
    with pytest.raises(ValueError):
        weighted_risk_contribution([0.01], [np.nan], [100])
    with pytest.raises(ValueError):
        weighted_risk_contribution([0.01], [0.2, 1], [100])


def test_runner_returns_both_hydraulic_sources_and_writes_no_files(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    results, comparison, curves, sensitivity = run_fragility_model(show_plots=False)
    assert len(results) == 80
    assert len(comparison) == 10
    assert comparison["Difference [m]"].abs().max() > 0.5
    assert results["Redesign macro rerun missing"].sum() == 60
    assert results["Macro source needs review"].sum() == 40
    assert curves["Combined screening [-]"].between(0, 1).all()
    assert sensitivity["Piping [-]"].between(0, 1).all()
    assert list(tmp_path.iterdir()) == []
