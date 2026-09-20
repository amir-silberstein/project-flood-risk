"""Simplified, volume-limited flood propagation for submodel 3."""

from collections import deque
from typing import TypeAlias

import numpy as np

from .spatial_areas import AreaMap, SpatialData, create_area_map

BreachCoordinate: TypeAlias = tuple[int, int]
BreachArea: TypeAlias = int | BreachCoordinate


def storage_volume_at_level(
    water_level_m: float,
    average_elevations_m: np.ndarray,
    cell_area_m2: float,
) -> float:
    """Estimate stored volume in cells up to an absolute water level.

    This is deliberately isolated as a replaceable assumption. Each cell is
    represented as a flat 100 m by 100 m storage area whose datum is its
    average elevation. The provided maximum elevation is used separately as
    the threshold for opening the next connected area.
    """
    submerged_height_m = np.maximum(water_level_m - average_elevations_m, 0.0)
    return float(np.sum(submerged_height_m) * cell_area_m2)


def _fill_area(
    area_id: int,
    available_volume_m3: float,
    area_map: AreaMap,
) -> tuple[float, float, bool]:
    coordinates = area_map.cell_coordinates[area_id]
    cell_indices = tuple(zip(*coordinates))
    average_elevations = area_map.average_elevation[cell_indices]
    maximum_elevations = area_map.maximum_elevation[cell_indices]
    valid = np.isfinite(average_elevations) & np.isfinite(maximum_elevations)
    average_elevations = average_elevations[valid]
    maximum_elevations = maximum_elevations[valid]
    if not average_elevations.size:
        return 0.0, 0.0, False

    cell_area_m2 = area_map.cell_size_m**2
    threshold_m = float(np.max(maximum_elevations))
    required_volume_m3 = storage_volume_at_level(
        threshold_m,
        average_elevations,
        cell_area_m2,
    )
    if available_volume_m3 >= required_volume_m3:
        return threshold_m, required_volume_m3, True

    lower_m = float(np.min(average_elevations))
    upper_m = threshold_m
    for _ in range(60):
        midpoint_m = (lower_m + upper_m) / 2
        midpoint_volume_m3 = storage_volume_at_level(
            midpoint_m,
            average_elevations,
            cell_area_m2,
        )
        if midpoint_volume_m3 <= available_volume_m3:
            lower_m = midpoint_m
        else:
            upper_m = midpoint_m

    water_level_m = lower_m
    return water_level_m, storage_volume_at_level(
        water_level_m,
        average_elevations,
        cell_area_m2,
    ), False


def _resolve_breach_area(breach_area: BreachArea, area_map: AreaMap) -> int:
    if isinstance(breach_area, tuple):
        y, x = breach_area
        if not (0 <= y < area_map.area_ids.shape[0] and 0 <= x < area_map.area_ids.shape[1]):
            raise ValueError("breach_area coordinates are outside the spatial grid")
        area_id = int(area_map.area_ids[y, x])
    else:
        area_id = int(breach_area)

    if area_id <= 0 or area_id not in area_map.cell_coordinates:
        raise ValueError("breach_area does not identify a valid spatial area")
    return area_id


def simulate_flood(
    breach_area: BreachArea,
    discharge_m3_per_s: float,
    event_time_s: float,
    spatial_data: SpatialData,
    area_map: AreaMap | None = None,
) -> np.ndarray:
    """Return absolute water level [m] for every cell in the spatial grid.

    ``discharge_m3_per_s * event_time_s`` is the available flood volume [m3].
    Unflooded and outside-domain cells are ``NaN``. The algorithm fills the
    breach area first, then visits edge-connected areas only after the current
    area's maximum-elevation threshold is reached.
    """
    if discharge_m3_per_s < 0 or event_time_s < 0:
        raise ValueError("discharge_m3_per_s and event_time_s must be non-negative")

    area_map = area_map or create_area_map(spatial_data)
    start_area = _resolve_breach_area(breach_area, area_map)
    available_volume_m3 = discharge_m3_per_s * event_time_s
    water_levels_m = np.full(area_map.area_ids.shape, np.nan, dtype=float)
    pending_areas = deque([start_area])
    visited_areas = {start_area}

    while pending_areas and available_volume_m3 > 0:
        area_id = pending_areas.popleft()
        water_level_m, used_volume_m3, reached_threshold = _fill_area(
            area_id,
            available_volume_m3,
            area_map,
        )
        available_volume_m3 -= used_volume_m3

        coordinates = area_map.cell_coordinates[area_id]
        for y, x in coordinates:
            average_elevation_m = area_map.average_elevation[y, x]
            if np.isfinite(average_elevation_m) and average_elevation_m < water_level_m:
                water_levels_m[y, x] = water_level_m

        if not reached_threshold:
            break

        for neighbor_id in sorted(area_map.neighbors.get(area_id, ())):
            if neighbor_id not in visited_areas:
                visited_areas.add(neighbor_id)
                pending_areas.append(neighbor_id)

    return water_levels_m
