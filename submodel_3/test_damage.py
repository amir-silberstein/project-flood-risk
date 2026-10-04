"""Tests for post-flood economic damage calculations."""

import math

import numpy as np

from submodel_3.damage import (
    Cell,
    calculate_cell_fatalities,
    calculate_cell_damage,
    calculate_flood_damage,
    calculate_land_use_damage,
    calculate_vehicle_damage,
    casualty_factor,
    summarize_damage,
)


def cell(depth: float, land_use: int, population: float = 10.0) -> Cell:
    return Cell(0, 0, depth, population, land_use, 1)


def test_zero_depth_has_no_damage() -> None:
    damaged = calculate_cell_damage(cell(0.0, 1))

    assert damaged.land_use_damage == 0.0
    assert damaged.vehicle_damage == 0.0
    assert damaged.damage == 0.0


def test_infrastructure_damage_at_multiple_depths() -> None:
    assert calculate_land_use_damage(cell(0.5, 1)) == 0.19 * 13_668.0 * 150.0
    assert calculate_land_use_damage(cell(2.0, 1)) == 0.28 * 13_668.0 * 150.0


def test_employee_damage_boundaries() -> None:
    for land_use, maximum in ((3, 537_416.67), (4, 16_850.0)):
        for depth in (0.0, 1.0, 3.0, 5.0, 1.000001, 3.000001, 5.000001):
            expected_fraction = (
                0.1 * depth
                if depth <= 1.0
                else 0.06 * depth + 0.04
                if depth <= 3.0
                else 0.39 * depth - 0.95
                if depth <= 5.0
                else 1.0
            )
            expected = expected_fraction * maximum * 56.0 if depth > 0 else 0.0
            assert math.isclose(
                calculate_land_use_damage(cell(depth, land_use)), expected
            )


def test_recreation_greenhouse_and_agriculture() -> None:
    fraction = min(2.0, 0.24 * 2.0 + 0.4, 0.07 * 2.0 + 0.75, 1.0)
    assert calculate_land_use_damage(cell(2.0, 5)) == fraction * 109_000.0
    assert calculate_land_use_damage(cell(2.0, 6)) == fraction * 441_000.0
    assert calculate_land_use_damage(cell(2.0, 7)) == fraction * 31_000.0


def test_water_and_nature_have_no_land_use_damage() -> None:
    assert calculate_land_use_damage(cell(4.0, 8)) == 0.0
    assert calculate_land_use_damage(cell(4.0, 9)) == 0.0


def test_vehicle_damage_is_independent_of_land_use() -> None:
    infrastructure = calculate_vehicle_damage(cell(2.0, 1, population=20.0))
    nature = calculate_vehicle_damage(cell(2.0, 9, population=20.0))

    assert infrastructure == nature
    assert infrastructure > 0.0


def test_casualty_factor_uses_mutually_exclusive_standard_method_branches() -> None:
    assert casualty_factor(4.0, 0.1, 2.0) == 1.0
    assert casualty_factor(5.0, 0.5, 0.0) == 1.0
    assert casualty_factor(2.0, 0.5, 0.0) == min(1.0, 1.45e-3 * np.exp(1.39 * 2.0))
    assert casualty_factor(1.0, 0.5, 0.0) == min(1.0, 1.34e-3 * np.exp(0.59))
    assert casualty_factor(2.0, 0.2, 0.0) == min(1.0, 1.34e-3 * np.exp(0.59 * 2.0))
    assert casualty_factor(0.0, 0.2, 0.0) == 0.0


def test_expected_fatalities_are_population_weighted() -> None:
    cells = [
        Cell(0, 0, 2.0, 100.0, 1, 1, rise_rate=0.5),
        Cell(0, 1, 1.0, 50.0, 1, 1, rise_rate=0.2),
    ]

    expected = (
        casualty_factor(2.0, 0.5, 0.0) * 100.0
        + casualty_factor(1.0, 0.2, 0.0) * 50.0
    )
    assert np.isclose(sum(calculate_cell_fatalities(cell) for cell in cells), expected)
    assert np.isclose(summarize_damage(cells)["expected_fatalities"], expected)


def test_total_damage_is_sum_and_summary_has_breakdowns() -> None:
    cells = calculate_flood_damage([cell(2.0, 1), cell(2.0, 8)])
    summary = summarize_damage(cells)

    assert all(np.isfinite(item.damage) for item in cells)
    assert all(item.damage == item.land_use_damage + item.vehicle_damage for item in cells)
    assert all(item.total_damage == item.damage for item in cells)
    assert summary["total_damage"] == sum(item.damage for item in cells)
    assert set(summary["by_compartment"]) == {1}


def test_residential_damage_uses_single_and_multi_family_fractions() -> None:
    single_family = -0.14897 * 1.0**2 + 0.32872 * 1.0
    multi_family = 1.0 - (1.0 - 1.0 / 6.0) ** 4
    expected = 20.2 * (0.64 * 241_000.0 * single_family + 0.36 * 172_000.0 * multi_family)

    assert math.isclose(calculate_land_use_damage(cell(1.0, 2)), expected)
    assert calculate_land_use_damage(cell(0.0, 2)) == 0.0
    assert calculate_land_use_damage(cell(7.0, 2)) == 20.2 * (
        0.64 * 241_000.0 + 0.36 * 172_000.0
    )