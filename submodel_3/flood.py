"""Volume-conserving flood propagation through six connected compartments."""

from collections.abc import Mapping
from typing import TypeAlias

import numpy as np

from .compartment_data import (
    COMPARTMENT_BORDERS,
    COMPARTMENT_CONNECTIONS,
    COMPARTMENT_IDS,
)
from .spatial_areas import AreaMap, SpatialData, create_area_map

BreachCoordinate: TypeAlias = tuple[int, int]
CELL_AREA_M2 = 10_000.0


def calculate_compartment_volume(
    water_surface_m: float,
    ground_elevations_m: np.ndarray,
    cell_area_m2: float = CELL_AREA_M2,
) -> float:
    """Return volume below an absolute water-surface elevation."""
    depths_m = np.maximum(water_surface_m - ground_elevations_m, 0.0)
    return float(np.sum(depths_m) * cell_area_m2)


def calculate_water_surface(
    volume_m3: float,
    ground_elevations_m: np.ndarray,
    cell_area_m2: float = CELL_AREA_M2,
) -> float:
    """Convert a compartment volume into an absolute water-surface elevation."""
    if volume_m3 <= 0 or ground_elevations_m.size == 0:
        return float(np.min(ground_elevations_m)) if ground_elevations_m.size else 0.0

    lower_m = float(np.min(ground_elevations_m))
    upper_m = max(lower_m + 1.0, float(np.max(ground_elevations_m)))
    while calculate_compartment_volume(upper_m, ground_elevations_m, cell_area_m2) < volume_m3:
        upper_m = upper_m * 2.0 if upper_m > 0 else upper_m + 1.0

    for _ in range(60):
        midpoint_m = (lower_m + upper_m) / 2.0
        if calculate_compartment_volume(midpoint_m, ground_elevations_m, cell_area_m2) < volume_m3:
            lower_m = midpoint_m
        else:
            upper_m = midpoint_m
    return (lower_m + upper_m) / 2.0


def identify_breach_compartment(breach: BreachCoordinate, area_map: AreaMap) -> int:
    """Return the compartment containing a ``(row, column)`` breach cell."""
    y, x = breach
    if not (0 <= y < area_map.area_ids.shape[0] and 0 <= x < area_map.area_ids.shape[1]):
        raise ValueError("breach coordinates are outside the spatial grid")
    compartment_id = int(area_map.area_ids[y, x])
    if compartment_id not in COMPARTMENT_IDS:
        raise ValueError("breach cell is outside the six flood compartments")
    return compartment_id


def _compartment_ground_elevations(area_map: AreaMap, compartment_id: int) -> np.ndarray:
    coordinates = area_map.cell_coordinates.get(compartment_id, ())
    if not coordinates:
        return np.array([], dtype=float)
    cell_indices = tuple(zip(*coordinates))
    elevations = area_map.average_elevation[cell_indices]
    return elevations[np.isfinite(elevations)]


def _water_surfaces(volumes_m3: Mapping[int, float], area_map: AreaMap) -> dict[int, float]:
    return {
        compartment_id: calculate_water_surface(
            volumes_m3.get(compartment_id, 0.0),
            _compartment_ground_elevations(area_map, compartment_id),
        )
        for compartment_id in COMPARTMENT_IDS
    }


def check_spill_conditions(
    volumes_m3: Mapping[int, float], area_map: AreaMap
) -> dict[tuple[int, int], float]:
    """Return spillable volume for each border currently reached."""
    surfaces_m = _water_surfaces(volumes_m3, area_map)
    spillable: dict[tuple[int, int], float] = {}
    for border, border_elevation_m in COMPARTMENT_BORDERS.items():
        source_id, _ = border
        ground_elevations = _compartment_ground_elevations(area_map, source_id)
        border_volume_m3 = calculate_compartment_volume(border_elevation_m, ground_elevations)
        if surfaces_m[source_id] >= border_elevation_m:
            spillable[border] = max(volumes_m3.get(source_id, 0.0) - border_volume_m3, 0.0)
    return spillable


def transfer_water_between_compartments(
    volumes_m3: dict[int, float], area_map: AreaMap
) -> bool:
    """Transfer available water over reached borders; return whether state changed."""
    changed = False
    surfaces_m = _water_surfaces(volumes_m3, area_map)
    for source_id in COMPARTMENT_IDS:
        reached = [
            target_id
            for target_id in COMPARTMENT_CONNECTIONS[source_id]
            if surfaces_m[source_id] >= COMPARTMENT_BORDERS[(source_id, target_id)]
        ]
        if not reached:
            continue

        border_level_m = min(
            COMPARTMENT_BORDERS[(source_id, target_id)] for target_id in reached
        )
        source_ground = _compartment_ground_elevations(area_map, source_id)
        retained_volume_m3 = calculate_compartment_volume(border_level_m, source_ground)
        excess_volume_m3 = max(volumes_m3[source_id] - retained_volume_m3, 0.0)
        if excess_volume_m3 <= 0:
            continue

        volumes_m3[source_id] = retained_volume_m3
        share_m3 = excess_volume_m3 / len(reached)
        for target_id in reached:
            volumes_m3[target_id] += share_m3
        changed = True
    return changed


def calculate_water_depths(volumes_m3: Mapping[int, float], area_map: AreaMap) -> np.ndarray:
    """Return non-negative relative water depth for every grid cell."""
    depths_m = np.zeros(area_map.area_ids.shape, dtype=float)
    surfaces_m = _water_surfaces(volumes_m3, area_map)
    for compartment_id in COMPARTMENT_IDS:
        for y, x in area_map.cell_coordinates.get(compartment_id, ()):
            ground_m = area_map.average_elevation[y, x]
            if np.isfinite(ground_m):
                depths_m[y, x] = max(surfaces_m[compartment_id] - ground_m, 0.0)
    return depths_m


def simulate_flood(
    breach: BreachCoordinate,
    discharge: float,
    time: float,
    spatial_data: SpatialData,
    area_map: AreaMap | None = None,
) -> np.ndarray:
    """Simulate flooding and return relative water depth [m] for the full grid."""
    if discharge < 0 or time < 0:
        raise ValueError("discharge and time must be non-negative")

    area_map = area_map or create_area_map(spatial_data)
    start_compartment = identify_breach_compartment(breach, area_map)
    volumes_m3 = {compartment_id: 0.0 for compartment_id in COMPARTMENT_IDS}
    volumes_m3[start_compartment] = discharge * time

    while transfer_water_between_compartments(volumes_m3, area_map):
        pass
    return calculate_water_depths(volumes_m3, area_map)
