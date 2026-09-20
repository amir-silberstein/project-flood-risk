"""Submodel 3: flood-area propagation."""

from .flood import simulate_flood
from .spatial_areas import SpatialData, load_spatial_data, create_area_map

__all__ = [
    "SpatialData",
    "create_area_map",
    "load_spatial_data",
    "simulate_flood",
]
