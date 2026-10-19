"""Compartment topology for the inundation model."""

import numpy as np
from scipy.ndimage import label

GRID_SHAPE: tuple[int, int] = (223, 983)

BOUNDARIES: list[list[tuple[int, int]]] = [
    [(878, 20), (859, 117), (854, 173)],
    [(788, 35), (791, 106), (765, 138)],
    [(655, 50), (657, 95), (673, 122)],
    [(489, 38), (575, 112), (584, 142)],
    [(310, 4), (368, 74), (419, 165), (447, 219)],
    [(244, 38), (340, 130), (419, 165)],
    [(859, 117), (791, 106), (657, 95), (575, 112), (419, 165)],
]

COMPARTMENT_IDS: tuple[int, ...] = tuple(range(1, 15))

# Absolute border elevations in metres NAP. Each pair is source -> target.
COMPARTMENT_BORDERS: dict[tuple[int, int], float] = {
    (6, 12): 12.0,
    (6, 5): 12.0,
    (5, 12): 10.0,
    (12, 11): 14.0,
    (5, 8): 10.0,
    (8, 11): 8.0,
    (11, 10): 11.0,
    (8, 4): 14.0,
    (4, 10): 6.5,
    (4, 7): 7.5,
    (10, 13): 12.0,
    (7, 13): 6.0,
    (13, 14): 4.0,
    (14, 9): 5.0,
    (7, 9): 3.0,
    (7, 1): 7.0,
    (1, 2): 3.0,
    (9, 2): 7.0,
    (2, 3): 3.0,
    (14, 3): 6.0,
}

COMPARTMENT_CONNECTIONS: dict[int, tuple[int, ...]] = {
    compartment_id: tuple(
        target_id
        for source_id, target_id in COMPARTMENT_BORDERS
        if source_id == compartment_id
    )
    for compartment_id in COMPARTMENT_IDS
}


def create_compartment_ids(dike_ring: np.ndarray) -> np.ndarray:
    """Create compartment IDs from the dike-ring raster and boundaries."""
    y, x = np.indices(dike_ring.shape)
    boundary_mask = np.zeros(dike_ring.shape, dtype=bool)

    for points in BOUNDARIES:
        for (x1, y1), (x2, y2) in zip(points[:-1], points[1:]):
            dx, dy = x2 - x1, y2 - y1
            distance_along_line = np.clip(
                ((x - x1) * dx + (y - y1) * dy) / (dx**2 + dy**2),
                0,
                1,
            )
            closest_x = x1 + distance_along_line * dx
            closest_y = y1 + distance_along_line * dy
            boundary_mask |= (
                np.hypot(x - closest_x, y - closest_y) < 0.75
            )

    compartment_ids = np.zeros(dike_ring.shape, dtype=int)
    next_id = 1

    for ring_id in np.unique(dike_ring[np.isfinite(dike_ring)]):
        ring = (dike_ring == ring_id) & ~boundary_mask
        regions, number_of_regions = label(
            ring,
            structure=np.array(
                [[0, 1, 0], [1, 1, 1], [0, 1, 0]]
            ),
        )

        for region_id in range(1, number_of_regions + 1):
            region = regions == region_id
            if np.sum(region) < 100:
                continue
            compartment_ids[region] = next_id
            next_id += 1

    return compartment_ids
