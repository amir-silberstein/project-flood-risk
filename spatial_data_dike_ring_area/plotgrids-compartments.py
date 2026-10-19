# -*- coding: utf-8 -*-
"""Data and compartment plotting for Project Flood Risk Module 5."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import BoundaryNorm, ListedColormap
from scipy.ndimage import label


# ==============================================================================
# 1. SETTINGS
# ==============================================================================

try:
    SCRIPT_DIR = Path(__file__).resolve().parent
except NameError:
    SCRIPT_DIR = Path.cwd()

GRID_SHAPE = (223, 983)


BOUNDARIES = [
    [(878, 20), (859, 117), (854, 173)],
    [(788, 35), (791, 106), (765, 138)],
    [(655, 50), (657, 95), (673, 122)],
    [(489, 38), (575, 112), (584, 142)],
    [(310, 4), (368, 74), (419, 165), (447, 219)],
    [(244, 38), (340, 130), (419, 165)],
    [(859, 117), (791, 106), (657, 95), (575, 112), (419, 165)],
]


# ==============================================================================
# 2. LOAD DATA
# ==============================================================================

def load_raster(filename: str) -> np.ndarray:
    """Load a semicolon-delimited raster."""
    return pd.read_csv(
        SCRIPT_DIR / filename,
        header=None,
        delimiter=";",
        encoding="utf-8-sig",
    ).to_numpy(dtype=float)


dike_ring = load_raster("Dikeringarea.txt")
ahn_max = load_raster("AHN_max.txt")

if dike_ring.shape != GRID_SHAPE or ahn_max.shape != GRID_SHAPE:
    raise ValueError(f"Expected raster dimensions {GRID_SHAPE}")


# ==============================================================================
# 3. ELEVATION MAP
# ==============================================================================

fig, ax = plt.subplots(figsize=(14, 5))

image = ax.imshow(
    ahn_max,
    cmap="terrain",
    origin="lower",
    extent=[0, 983, 0, 223],
    aspect="auto",
)

fig.colorbar(image, ax=ax, label="Elevation [m + NAP]")
ax.set(title="Maximum Elevation", xlabel="x coordinate", ylabel="y coordinate")
fig.tight_layout()


# ==============================================================================
# 4. DIKE RING AREAS
# ==============================================================================

fig2, ax2 = plt.subplots(figsize=(14, 5))

ax2.imshow(
    dike_ring,
    cmap="tab10",
    origin="lower",
    extent=[0, 983, 0, 223],
    interpolation="nearest",
    aspect="auto",
)

ax2.set(title="Dike Ring Areas", xlabel="x coordinate", ylabel="y coordinate")
fig2.tight_layout()


# ==============================================================================
# 5. CREATE AND PLOT COMPARTMENTS
# ==============================================================================

y, x = np.indices(GRID_SHAPE)
boundary_mask = np.zeros(GRID_SHAPE, dtype=bool)

# Rasterize each polyline as a barrier.
for points in BOUNDARIES:
    for (x1, y1), (x2, y2) in zip(points[:-1], points[1:]):
        dx, dy = x2 - x1, y2 - y1
        length_squared = dx**2 + dy**2

        t = np.clip(
            ((x - x1) * dx + (y - y1) * dy) / length_squared,
            0,
            1,
        )
        distance = np.hypot(x - (x1 + t * dx), y - (y1 + t * dy))
        boundary_mask |= distance < 0.75

# Label connected regions separately within each dike ring.
compartment = np.zeros(GRID_SHAPE, dtype=int)
next_id = 1

for ring_id in np.unique(dike_ring[np.isfinite(dike_ring)]):
    ring_mask = (dike_ring == ring_id) & ~boundary_mask
    regions, count = label(
        ring_mask,
        structure=np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]]),
    )

    regions[regions > 0] += next_id - 1
    compartment[ring_mask] = regions[ring_mask]
    next_id += count

# Plot each compartment in a distinct color.
colors = plt.get_cmap("tab20", max(next_id, 2))
cmap = ListedColormap(["black"] + [colors(i) for i in range(next_id)])
norm = BoundaryNorm(np.arange(-1, next_id + 1), cmap.N)

plot_data = np.ma.masked_where(
    (compartment == 0) & ~boundary_mask,
    np.where(boundary_mask, -1, compartment),
)

fig3, ax3 = plt.subplots(figsize=(16, 6))

ax3.imshow(
    plot_data,
    cmap=cmap,
    norm=norm,
    origin="lower",
    extent=[0, 983, 0, 223],
    interpolation="nearest",
    aspect="auto",
)

for points in BOUNDARIES:
    bx, by = zip(*points)
    ax3.plot(bx, by, color="black", linewidth=1.5, marker=".", markersize=3)

for compartment_id in range(1, next_id):
    y, x = np.where(compartment == compartment_id)

    if len(x) == 0:
        continue

    ax.text(
        x.mean(),
        y.mean(),
        str(compartment_id),
        color="white",
        fontsize=9,
        fontweight="bold",
        ha="center",
        va="center",
        bbox=dict(
            facecolor="black",
            alpha=0.75,
            boxstyle="circle,pad=0.25",
        ),
    )

ax3.set(
    title=f"Detected Compartments ({next_id - 1} regions)",
    xlabel="x coordinate",
    ylabel="y coordinate",
    xlim=(0, 983),
    ylim=(0, 223),
)
fig3.tight_layout()

plt.show()