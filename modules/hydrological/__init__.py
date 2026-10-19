"""Hydrological and dike-breach calculations.

The package exposes the model's public calculation functions at the package
level so callers do not need to depend on the internal module layout.
"""

from dike_settings import DIKE16, DIKE43, DikeSettings

from .breach import calculate_breach_discharge
from .hydrological_table import create_hydrological_table
from .water_level import calculate_water_level

__all__ = [
    "DIKE16",
    "DIKE43",
    "DikeSettings",
    "calculate_breach_discharge",
    "calculate_water_level",
    "create_hydrological_table",
]
