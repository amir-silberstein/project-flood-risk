"""Calculate economic flood damage from final flood depths.

Damage is calculated after flood propagation has completed. The model grid
uses one-hectare cells, so values given per hectare are applied directly to a
cell without an area conversion.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import Final, TypeAlias

import numpy as np

from .spatial_areas import AreaMap, SpatialData

ResidentialDamageFunction: TypeAlias = Callable[[float], float]

LAND_USE_NAMES: Final[dict[int, str]] = {
    1: "Infrastructure",
    2: "Residential",
    3: "Industry/commercial",
    4: "Government institutions/services",
    5: "Recreation",
    6: "Greenhouses",
    7: "Agriculture",
    8: "Water",
    9: "Nature",
}


@dataclass
class Cell:
    """One grid cell and its post-flood damage properties."""

    row: int
    column: int
    depth: float
    population: float
    land_use: int
    compartment: int
    rise_rate: float = 0.0
    velocity: float = 0.0
    land_use_damage: float = 0.0
    vehicle_damage: float = 0.0
    damage: float = 0.0
    total_damage: float = 0.0


def casualty_factor(depth: float, rise_rate: float, velocity: float) -> float:
    """Return the Dutch Standard Method fatality factor for one cell."""
    if not all(np.isfinite(value) for value in (depth, rise_rate, velocity)):
        return 0.0
    if depth * velocity >= 7.0 and velocity >= 2.0:
        factor = 1.0
    elif rise_rate >= 0.5:
        if depth > 4.7:
            factor = 1.0
        elif depth >= 1.5:
            factor = 1.45e-3 * np.exp(1.39 * depth)
        else:
            factor = 1.34e-3 * np.exp(0.59 * depth)
    elif rise_rate < 0.5 and depth > 0:
        factor = 1.34e-3 * np.exp(0.59 * depth)
    else:
        factor = 0.0
    return float(np.clip(factor, 0.0, 1.0))


def calculate_cell_fatalities(cell: Cell) -> float:
    """Return expected fatal casualties for one cell."""
    population = float(cell.population)
    if not np.isfinite(population) or population <= 0:
        return 0.0
    return casualty_factor(cell.depth, cell.rise_rate, cell.velocity) * population


def _depth_curve(depth: float) -> float:
    return min(depth, 0.24 * depth + 0.4, 0.07 * depth + 0.75, 1.0)


def _single_family_damage_fraction(depth: float) -> float:
    if depth <= 0:
        return 0.0
    if depth <= 1:
        return -0.14897 * depth**2 + 0.32872 * depth
    if depth <= 2:
        return 0.00342 * depth**2 + 0.04024 * depth + 0.13946
    if depth <= 4:
        return 0.03232 * depth**2 + 0.05303 * depth - 0.00168
    if depth <= 5:
        return -0.27246 * depth**2 + 2.72460 * depth - 5.81189
    return 1.0


def _multi_family_damage_fraction(depth: float) -> float:
    if depth <= 0:
        return 0.0
    if depth <= 6:
        return 1.0 - (1.0 - depth / 6.0) ** 4
    return 1.0


def _employee_damage(depth: float, employees: float, maximum_damage: float) -> float:
    if depth <= 1.0:
        fraction = 0.1 * depth
    elif depth <= 3.0:
        fraction = 0.06 * depth + 0.04
    elif depth <= 5.0:
        fraction = 0.39 * depth - 0.95
    else:
        fraction = 1.0
    return fraction * maximum_damage * employees


def calculate_land_use_damage(
    cell: Cell
) -> float:
    """Return land-use damage in euros for one cell.

    Residential damage combines the supplied single-family and multi-family
    depth-damage fractions using the existing 64%/36% building mix.
    """
    MF = 172000.0
    SF = 241000.0

    depth = float(cell.depth)
    if not np.isfinite(depth) or depth <= 0:
        return 0.0

    land_use = cell.land_use
    if land_use == 1:
        fraction = min(depth, 0.28, 0.18 * depth + 0.1, 1.0)
        return fraction * 13_668.0 * 150.0
    if land_use == 2:
        return 20.2 * (
            0.64 * SF * _single_family_damage_fraction(depth)
            + 0.36 * MF * _multi_family_damage_fraction(depth)
        )
    if land_use == 3:
        return _employee_damage(depth, employees=56.0, maximum_damage=537_416.67)
    if land_use == 4:
        return _employee_damage(depth, employees=56.0, maximum_damage=16_850.0)
    if land_use == 5:
        return _depth_curve(depth) * 109_000.0
    if land_use == 6:
        return _depth_curve(depth) * 441_000.0
    if land_use == 7:
        return _depth_curve(depth) * 31_000.0
    if land_use in (8, 9):
        return 0.0
    raise ValueError(f"Unsupported land-use code: {land_use}")


def calculate_vehicle_damage(cell: Cell) -> float:
    """Return vehicle damage in euros for one cell."""
    depth = float(cell.depth)
    if not np.isfinite(depth) or depth <= 0:
        return 0.0
    fraction = min(
        abs(0.17 * depth - 0.03),
        abs(0.72 * depth - 0.3),
        abs(0.31 * depth + 0.1),
        1.0,
    )
    return 0.48 * float(cell.population) * fraction * 1_070.0


def calculate_cell_damage(
    cell: Cell,
) -> Cell:
    """Calculate and store all damage properties on one cell."""
    land_use_damage = calculate_land_use_damage(cell)
    vehicle_damage = calculate_vehicle_damage(cell)
    cell.land_use_damage = land_use_damage
    cell.vehicle_damage = vehicle_damage
    cell.damage = land_use_damage + vehicle_damage
    cell.total_damage = cell.damage
    return cell


def cells_from_flood(
    depths_m: np.ndarray,
    spatial_data: SpatialData,
    area_map: AreaMap,
) -> list[Cell]:
    """Build damage cells from the final depth grid and existing model arrays."""
    if spatial_data.inhabitants is None:
        raise ValueError("Population data is required for vehicle damage")
    if depths_m.shape != spatial_data.land_use.shape:
        raise ValueError("depths_m and spatial data must have the same shape")

    cells: list[Cell] = []
    for compartment_id, coordinates in area_map.compartments.items():
        for row, column in coordinates:
            land_use = spatial_data.land_use[row, column]
            population = spatial_data.inhabitants[row, column]
            if not np.isfinite(land_use):
                continue
            cells.append(
                Cell(
                    row=row,
                    column=column,
                    depth=float(depths_m[row, column]),
                    population=float(population) if np.isfinite(population) else 0.0,
                    land_use=int(round(land_use)),
                    compartment=compartment_id,
                )
            )
    return cells


def calculate_flood_damage(
    cells: Iterable[Cell],
) -> list[Cell]:
    """Calculate damage after the final flood depths have been assigned."""
    calculated_cells = list(cells)
    for cell in calculated_cells:
        calculate_cell_damage(cell)
    return calculated_cells


def summarize_damage(cells: Iterable[Cell]) -> dict[str, object]:
    """Aggregate damage overall, by land use, and by compartment."""
    cells = list(cells)
    by_land_use: dict[str, dict[str, float]] = {}
    by_compartment: dict[int, dict[str, float]] = {}
    expected_fatalities = 0.0
    casualty_factors: list[float] = []
    exposed_population = 0.0
    flooded_exposed_population = 0.0
    for cell in cells:
        land_use_name = LAND_USE_NAMES.get(cell.land_use, f"Unknown ({cell.land_use})")
        land_use_totals = by_land_use.setdefault(
            land_use_name,
            {
                "land_use_damage": 0.0,
                "vehicle_damage": 0.0,
                "total_damage": 0.0,
                "expected_fatalities": 0.0,
            },
        )
        compartment_totals = by_compartment.setdefault(
            cell.compartment,
            {
                "land_use_damage": 0.0,
                "vehicle_damage": 0.0,
                "total_damage": 0.0,
                "expected_fatalities": 0.0,
            },
        )
        cell_population = float(cell.population)
        if np.isfinite(cell_population) and cell_population > 0:
            exposed_population += cell_population
            if cell.depth > 0:
                flooded_exposed_population += cell_population
        cell_factor = casualty_factor(cell.depth, cell.rise_rate, cell.velocity)
        valid_population = cell_population if np.isfinite(cell_population) and cell_population > 0 else 0.0
        cell_fatalities = cell_factor * valid_population
        expected_fatalities += cell_fatalities
        casualty_factors.append(cell_factor)
        for totals in (land_use_totals, compartment_totals):
            totals["land_use_damage"] += cell.land_use_damage
            totals["vehicle_damage"] += cell.vehicle_damage
            totals["total_damage"] += cell.damage
            totals["expected_fatalities"] += cell_fatalities
    return {
        "cells": len(cells),
        "flooded_cells": sum(cell.depth > 0 for cell in cells),
        "exposed_population": exposed_population,
        "flooded_exposed_population": flooded_exposed_population,
        "land_use_damage": sum(cell.land_use_damage for cell in cells),
        "vehicle_damage": sum(cell.vehicle_damage for cell in cells),
        "total_damage": sum(cell.damage for cell in cells),
        "expected_fatalities": expected_fatalities,
        "average_casualty_factor": (
            float(np.mean(casualty_factors)) if casualty_factors else 0.0
        ),
        "maximum_casualty_factor": max(casualty_factors, default=0.0),
        "by_land_use": by_land_use,
        "by_compartment": by_compartment,
    }


def print_damage_summary(cells: Iterable[Cell]) -> None:
    """Print aggregate damage totals and breakdowns."""
    summary = summarize_damage(cells)
    print("\nFlood damage summary")
    print("=" * 72)
    print(f"Cells: {summary['cells']:,}")
    print(f"Flooded cells: {summary['flooded_cells']:,}")
    print(f"Exposed population: {summary['exposed_population']:,.0f}")
    print(f"Flooded exposed population: {summary['flooded_exposed_population']:,.0f}")
    print(f"Land-use damage: €{summary['land_use_damage']:,.2f}")
    print(f"Vehicle damage: €{summary['vehicle_damage']:,.2f}")
    print(f"Total damage: €{summary['total_damage']:,.2f}")
    print(f"Expected fatal casualties: {summary['expected_fatalities']:,.2f}")
    print(f"Average casualty factor: {summary['average_casualty_factor']:.6f}")
    print(f"Maximum casualty factor: {summary['maximum_casualty_factor']:.6f}")
    print("\nBy land use:")
    print("  Land use                                      Land-use        Vehicle          Total  Fatalities")
    for land_use, damage in summary["by_land_use"].items():
        print(
            f"  {land_use:<44}"
            f"€{damage['land_use_damage']:>12,.2f}"
            f"  €{damage['vehicle_damage']:>12,.2f}"
            f"  €{damage['total_damage']:>12,.2f}"
            f"  {damage['expected_fatalities']:>10,.2f}"
        )
    print("By compartment:")
    print("  Compartment                                  Land-use        Vehicle          Total  Fatalities")
    for compartment, damage in sorted(summary["by_compartment"].items()):
        print(
            f"  {compartment:<44}"
            f"€{damage['land_use_damage']:>12,.2f}"
            f"  €{damage['vehicle_damage']:>12,.2f}"
            f"  €{damage['total_damage']:>12,.2f}"
            f"  {damage['expected_fatalities']:>10,.2f}"
        )