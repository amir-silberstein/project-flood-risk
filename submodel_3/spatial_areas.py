"""Load the existing spatial rasters and build a connected area map."""

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

import numpy as np
import pandas as pd


DEFAULT_DATA_DIRECTORY = (
    Path(__file__).resolve().parent.parent / "spatial_data_dike_ring_area"
)


@dataclass(frozen=True)
class SpatialData:
    """Spatial rasters using the existing ``[y, x]`` matrix convention."""

    dike_ring: np.ndarray
    maximum_elevation: np.ndarray
    average_elevation: np.ndarray
    land_use: np.ndarray
    inhabitants: np.ndarray | None = None
    cell_size_m: float = 100.0

    def __post_init__(self) -> None:
        arrays = (
            self.dike_ring,
            self.maximum_elevation,
            self.average_elevation,
            self.land_use,
        )
        if self.inhabitants is not None:
            arrays += (self.inhabitants,)
        if any(array.shape != self.dike_ring.shape for array in arrays):
            raise ValueError("All spatial rasters must have the same shape")
        if self.cell_size_m <= 0:
            raise ValueError("cell_size_m must be positive")


@dataclass(frozen=True)
class AreaMap:
    """Area labels, cell coordinates, elevations, and area adjacency."""

    area_ids: np.ndarray
    cell_coordinates: Mapping[int, tuple[tuple[int, int], ...]]
    neighbors: Mapping[int, frozenset[int]]
    maximum_elevation: np.ndarray
    average_elevation: np.ndarray
    cell_size_m: float


def _read_raster(path: Path) -> np.ndarray:
    """Read the project's semicolon-delimited raster, including its BOM."""
    return pd.read_csv(
        path,
        header=None,
        delimiter=";",
        encoding="utf-8-sig",
    ).to_numpy(dtype=float)


def load_spatial_data(data_directory: str | Path = DEFAULT_DATA_DIRECTORY) -> SpatialData:
    """Load the existing dike-ring, elevation, land-use, and population rasters."""
    directory = Path(data_directory)
    return SpatialData(
        dike_ring=_read_raster(directory / "Dikeringarea.txt"),
        maximum_elevation=_read_raster(directory / "AHN_max.txt"),
        average_elevation=_read_raster(directory / "AHN_avg.txt"),
        land_use=_read_raster(directory / "Landuse.txt"),
        inhabitants=_read_raster(directory / "Inhabitants.txt"),
    )


def _existing_compartments(dike_ring: np.ndarray) -> np.ndarray:
    """Apply the six compartment rules already used by the spatial script."""
    rows, columns = dike_ring.shape
    y_indices, x_indices = np.indices(dike_ring.shape)
    compartments = np.zeros(dike_ring.shape, dtype=int)
    valid = np.isfinite(dike_ring)

    ring_43 = valid & (dike_ring == 43)
    compartments[ring_43 & (y_indices > rows * (800 - x_indices) / 100)] = 1
    ring_43_remaining = ring_43 & (compartments == 0)
    compartments[
        ring_43_remaining & (y_indices > rows * (x_indices - 400) / 150)
    ] = 2
    compartments[ring_43 & (compartments == 0)] = 3

    ring_16 = valid & (dike_ring == 16)
    compartments[ring_16 & (x_indices > 150) & (y_indices > 100)] = 4
    compartments[ring_16 & (x_indices > 150) & (y_indices <= 100)] = 5
    compartments[ring_16 & (x_indices <= 150)] = 6

    return compartments


def _area_labels(dike_ring: np.ndarray) -> np.ndarray:
    """Use existing compartments, or finite raster labels for artificial inputs."""
    finite_values = dike_ring[np.isfinite(dike_ring)]
    if finite_values.size and set(np.unique(finite_values)).issubset({16.0, 43.0}):
        return _existing_compartments(dike_ring)

    labels = np.zeros(dike_ring.shape, dtype=int)
    labels[np.isfinite(dike_ring)] = np.rint(dike_ring[np.isfinite(dike_ring)]).astype(int)
    return labels


def _area_neighbors(area_ids: np.ndarray) -> dict[int, frozenset[int]]:
    """Find areas sharing an edge; diagonal-only contact is not connected."""
    neighbors = {int(area_id): set() for area_id in np.unique(area_ids) if area_id > 0}
    for axis in (0, 1):
        left = np.take(area_ids, indices=range(area_ids.shape[axis] - 1), axis=axis)
        right = np.take(area_ids, indices=range(1, area_ids.shape[axis]), axis=axis)
        touching = (left != right) & (left > 0) & (right > 0)
        for first, second in zip(left[touching], right[touching]):
            neighbors[int(first)].add(int(second))
            neighbors[int(second)].add(int(first))
    return {area_id: frozenset(area_neighbors) for area_id, area_neighbors in neighbors.items()}


def create_area_map(spatial_data: SpatialData) -> AreaMap:
    """Create area labels and connectivity from existing raster coordinates."""
    area_ids = _area_labels(spatial_data.dike_ring)
    coordinates = {
        int(area_id): tuple(map(tuple, np.argwhere(area_ids == area_id)))
        for area_id in np.unique(area_ids)
        if area_id > 0
    }
    return AreaMap(
        area_ids=area_ids,
        cell_coordinates=coordinates,
        neighbors=_area_neighbors(area_ids),
        maximum_elevation=spatial_data.maximum_elevation,
        average_elevation=spatial_data.average_elevation,
        cell_size_m=spatial_data.cell_size_m,
    )
