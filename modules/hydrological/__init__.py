"""Hydrological model package."""

from .Dike16_water_level import calculate_water_level as calculate_dike16_water_level
from .Dike43_water_level import calculate_water_level as calculate_dike43_water_level
from .hydrological_model import create_hydrological_table

__all__ = [
    "calculate_dike16_water_level",
    "calculate_dike43_water_level",
    "create_hydrological_table",
]
