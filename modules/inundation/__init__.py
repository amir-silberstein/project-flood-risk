"""Public API for the inundation model."""

from .compartment_data import (
    BOUNDARIES,
    COMPARTMENT_BORDERS,
    COMPARTMENT_CONNECTIONS,
    COMPARTMENT_IDS,
    GRID_SHAPE,
    create_compartment_ids,
)
from .inundation import create_inundation_table

__all__ = [
    "BOUNDARIES",
    "COMPARTMENT_BORDERS",
    "COMPARTMENT_CONNECTIONS",
    "COMPARTMENT_IDS",
    "GRID_SHAPE",
    "INUNDATION_CELL_AREA",
    "create_compartment_ids",
    "create_inundation_table",
]
