"""Behavior checks for the simplified flood-area model."""

import numpy as np

from submodel_3.flood import simulate_flood
from submodel_3.spatial_areas import SpatialData, create_area_map


def artificial_spatial_data() -> SpatialData:
    """Create three areas: two connected and one separated by outside cells."""
    dike_ring = np.array(
        [
            [1, 1, 2, 2, np.nan, 3],
            [1, 1, 2, 2, np.nan, 3],
        ],
        dtype=float,
    )
    maximum_elevation = np.array(
        [
            [2, 2, 5, 5, np.nan, 1],
            [2, 2, 5, 5, np.nan, 1],
        ],
        dtype=float,
    )
    average_elevation = np.where(np.isfinite(dike_ring), 0.0, np.nan)
    land_use = np.where(np.isfinite(dike_ring), 1.0, np.nan)
    return SpatialData(
        dike_ring=dike_ring,
        maximum_elevation=maximum_elevation,
        average_elevation=average_elevation,
        land_use=land_use,
        cell_size_m=1.0,
    )


def test_breach_fills_before_connected_area() -> None:
    spatial_data = artificial_spatial_data()
    water_levels = simulate_flood((0, 0), 1.0, 4.0, spatial_data)

    assert np.all(np.isfinite(water_levels[0:2, 0:2]))
    assert np.all(np.isnan(water_levels[0:2, 2:4]))
    assert np.all(np.isnan(water_levels[:, 5]))


def test_connected_area_starts_after_breach_threshold() -> None:
    spatial_data = artificial_spatial_data()
    water_levels = simulate_flood((0, 0), 1.0, 12.0, spatial_data)

    assert np.all(water_levels[0:2, 0:2] == 2.0)
    assert np.all(water_levels[0:2, 2:4] == 1.0)
    assert np.all(np.isnan(water_levels[:, 5]))


def test_output_shape_and_stable_state() -> None:
    spatial_data = artificial_spatial_data()
    area_map = create_area_map(spatial_data)
    water_levels = simulate_flood(1, 100.0, 100.0, spatial_data, area_map)

    assert water_levels.shape == spatial_data.dike_ring.shape
    assert area_map.neighbors[1] == frozenset({2})
    assert area_map.neighbors[2] == frozenset({1})
    assert 3 not in area_map.neighbors[1]
    assert np.all(np.isnan(water_levels[:, 4]))
    assert np.all(np.isnan(water_levels[:, 5]))
