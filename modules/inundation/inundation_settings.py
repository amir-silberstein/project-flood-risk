"""Inundation scenario settings."""

from .compartment_data import COMPARTMENT_BORDERS

COMPARTMENT_BORDERS_RAISED = {
    **COMPARTMENT_BORDERS,
    (2, 3): 4.0,
    (6, 5): 13.0,
}
