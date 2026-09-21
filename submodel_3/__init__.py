"""Submodel 3: flood-area propagation."""

from .flood import (
    BreachCoordinate,
    calculate_water_depths,
    identify_breach_compartment,
    simulate_flood,
)
from .spatial_areas import SpatialData, load_spatial_data, create_area_map
from .visualization import calculate_flood_progression, plot_flood_progression

__all__ = [
    "SpatialData",
    "create_area_map",
    "load_spatial_data",
    "simulate_flood",
    "BreachCoordinate",
    "calculate_water_depths",
    "identify_breach_compartment",
    "calculate_flood_progression",
    "plot_flood_progression",
]
