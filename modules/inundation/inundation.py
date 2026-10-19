"""Compartment-based inundation model."""

from pathlib import Path

import numpy as np
import pandas as pd

from global_settings import FLOOD_DURATION
from dike_settings import DikeSettings

from .compartment_data import (
    COMPARTMENT_BORDERS,
    COMPARTMENT_CONNECTIONS,
    COMPARTMENT_IDS,
    create_compartment_ids,
)

INUNDATION_CELL_AREA: float = 10_000.0  # m^2, one hectare per cell

DATA_DIRECTORY = (
    Path(__file__).resolve().parents[2] / "spatial_data_dike_ring_area"
)


def _load_raster(filename: str, data_directory: Path) -> np.ndarray:
    return pd.read_csv(
        data_directory / filename,
        header=None,
        sep=";",
        encoding="utf-8-sig",
    ).to_numpy(dtype=float)


def _read_input_rasters(
    data_directory: Path,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    return (
        _load_raster("Dikeringarea.txt", data_directory),
        _load_raster("AHN_avg.txt", data_directory),
        _load_raster("Landuse.txt", data_directory),
        _load_raster("Inhabitants.txt", data_directory),
    )


def _water_volume(surface_m: float, elevations_m: np.ndarray) -> float:
    depth_m = np.maximum(surface_m - elevations_m, 0)
    return float(depth_m.sum() * INUNDATION_CELL_AREA)


def _water_surface(volume_m3: float, elevations_m: np.ndarray) -> float:
    elevations_m = elevations_m[np.isfinite(elevations_m)]
    if len(elevations_m) == 0:
        return 0.0

    lowest_m = float(elevations_m.min())
    highest_m = max(lowest_m + 1, float(elevations_m.max()))

    while _water_volume(highest_m, elevations_m) < volume_m3:
        highest_m *= 2

    for _ in range(50):
        middle_m = (lowest_m + highest_m) / 2
        if _water_volume(middle_m, elevations_m) < volume_m3:
            lowest_m = middle_m
        else:
            highest_m = middle_m

    return (lowest_m + highest_m) / 2


def _compartment_elevations(
    compartment_ids: np.ndarray,
    elevations_m: np.ndarray,
) -> dict[int, np.ndarray]:
    return {
        compartment_id: elevations_m[compartment_ids == compartment_id]
        for compartment_id in COMPARTMENT_IDS
    }


def _spill_water(
    volumes_m3: dict[int, float],
    elevations: dict[int, np.ndarray],
) -> None:
    """Keep spilling water until every reached border has been processed."""
    water_moved = True

    while water_moved:
        water_moved = False
        surfaces_m = {
            compartment_id: _water_surface(
                volumes_m3[compartment_id],
                elevations[compartment_id],
            )
            for compartment_id in COMPARTMENT_IDS
        }

        for source_id in COMPARTMENT_IDS:
            reached = [
                target_id
                for target_id in COMPARTMENT_CONNECTIONS[source_id]
                if surfaces_m[source_id]
                >= COMPARTMENT_BORDERS[(source_id, target_id)]
            ]
            if not reached:
                continue

            lowest_border_m = min(
                COMPARTMENT_BORDERS[(source_id, target_id)]
                for target_id in reached
            )
            volume_at_border_m3 = _water_volume(
                lowest_border_m,
                elevations[source_id],
            )
            excess_m3 = volumes_m3[source_id] - volume_at_border_m3
            if excess_m3 <= 0:
                continue

            volumes_m3[source_id] = volume_at_border_m3
            for target_id in reached:
                volumes_m3[target_id] += excess_m3 / len(reached)
            water_moved = True


def _create_cell_table(
    land_use: np.ndarray,
    population: np.ndarray,
    water_depth: np.ndarray,
) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "land use type": land_use.ravel(),
            "population": population.ravel(),
            "water depth": water_depth.ravel(),
        }
    )


def create_inundation_table(
    hydrological_table: pd.DataFrame,
    dike: DikeSettings,
    data_directory: str | Path = DATA_DIRECTORY,
) -> pd.DataFrame:
    """Create one cell-map DataFrame for every return period."""
    dike_ring, elevations_m, land_use, population = _read_input_rasters(
        Path(data_directory)
    )
    compartment_ids = create_compartment_ids(dike_ring)
    elevations = _compartment_elevations(compartment_ids, elevations_m)
    inundation_tables = []

    for _, hydrological_row in hydrological_table.iterrows():
        return_period = hydrological_row["return period [years]"]
        discharge = hydrological_row["breach discharge [m^3/s]"]
        total_volume_m3 = discharge * FLOOD_DURATION

        volumes_m3 = {compartment_id: 0.0 for compartment_id in COMPARTMENT_IDS}
        volumes_m3[dike.compartment_id] = total_volume_m3
        _spill_water(volumes_m3, elevations)

        water_surfaces_m = {
            compartment_id: _water_surface(
                volumes_m3[compartment_id],
                elevations[compartment_id],
            )
            for compartment_id in COMPARTMENT_IDS
        }
        water_depth = np.zeros(elevations_m.shape)

        for compartment_id in COMPARTMENT_IDS:
            cells = compartment_ids == compartment_id
            water_depth[cells] = np.maximum(
                water_surfaces_m[compartment_id] - elevations_m[cells],
                0,
            )

        inundation_tables.append(
            {
                "return period [years]": return_period,
                "map": _create_cell_table(land_use, population, water_depth),
            }
        )

    return pd.DataFrame(inundation_tables)