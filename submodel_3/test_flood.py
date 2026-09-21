"""Tests for six-compartment flood propagation."""

import numpy as np

from submodel_3.flood import (
    CELL_AREA_M2,
    calculate_compartment_volume,
    identify_breach_compartment,
    simulate_flood,
)
from submodel_3.spatial_areas import SpatialData, create_area_map


def synthetic_spatial_data() -> SpatialData:
    """Create one cell for each compartment and one outside-domain cell."""
    dike_ring = np.array([[1, 2, 3, 4, 5, 6, np.nan]], dtype=float)
    elevations = np.zeros_like(dike_ring)
    elevations[0, -1] = np.nan
    return SpatialData(
        dike_ring=dike_ring,
        maximum_elevation=elevations,
        average_elevation=elevations,
        land_use=np.where(np.isfinite(dike_ring), 1.0, np.nan),
    )


def test_breach_compartment_is_identified_from_location() -> None:
    area_map = create_area_map(synthetic_spatial_data())

    assert identify_breach_compartment((0, 0), area_map) == 1
    assert identify_breach_compartment((0, 4), area_map) == 5


def test_water_initially_remains_in_breach_compartment() -> None:
    depths_m = simulate_flood((0, 0), 10_000.0, 10.0, synthetic_spatial_data())

    assert depths_m[0, 0] == 10.0
    assert np.all(depths_m[0, 1:] == 0.0)


def test_water_does_not_spill_before_border_elevation() -> None:
    depths_m = simulate_flood((0, 0), 10_000.0, 14.9, synthetic_spatial_data())

    assert np.isclose(depths_m[0, 0], 14.9)
    assert np.all(depths_m[0, 1:] == 0.0)


def test_water_spills_to_next_compartment_at_border() -> None:
    depths_m = simulate_flood((0, 0), 10_000.0, 16.0, synthetic_spatial_data())

    assert depths_m[0, 0] == 15.0
    assert depths_m[0, 1] == 1.0
    assert np.all(depths_m[0, 2:] == 0.0)


def test_compartment_three_spills_to_both_four_and_five() -> None:
    depths_m = simulate_flood((0, 0), 10_000.0, 35.0, synthetic_spatial_data())

    assert depths_m[0, 2] == 10.0
    assert depths_m[0, 3] == 1.0
    assert depths_m[0, 4] == 1.0


def test_compartments_four_and_five_contribute_to_six() -> None:
    depths_m = simulate_flood((0, 0), 10_000.0, 45.0, synthetic_spatial_data())

    assert depths_m[0, 3] == 5.0
    assert depths_m[0, 4] == 5.0
    assert depths_m[0, 5] == 2.0


def test_output_is_nonnegative_full_grid_with_zero_unflooded_cells() -> None:
    depths_m = simulate_flood((0, 0), 0.0, 100.0, synthetic_spatial_data())

    assert depths_m.shape == (1, 7)
    assert np.all(depths_m >= 0.0)
    assert np.all(depths_m == 0.0)


def test_total_water_volume_is_conserved() -> None:
    discharge_m3_per_s = 10_000.0
    event_time_s = 45.0
    depths_m = simulate_flood(
        (0, 0), discharge_m3_per_s, event_time_s, synthetic_spatial_data()
    )

    assert np.isclose(np.sum(depths_m) * CELL_AREA_M2, discharge_m3_per_s * event_time_s)
    assert np.isclose(calculate_compartment_volume(5.0, np.array([0.0])), 50_000.0)
