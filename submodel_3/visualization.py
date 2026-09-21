"""Optional graphical views of Submodel 3 flood progression outputs."""

from collections.abc import Sequence

import numpy as np

from .flood import BreachCoordinate, CELL_AREA_M2, simulate_flood
from .spatial_areas import AreaMap, SpatialData


def calculate_flood_progression(
    breach: BreachCoordinate,
    discharge: float,
    event_times_s: Sequence[float],
    spatial_data: SpatialData,
    area_map: AreaMap | None = None,
) -> tuple[np.ndarray, ...]:
    """Collect flood outputs at successive event times.

    This function deliberately leaves ``flood.py`` unchanged: each progression
    frame is the output of the existing ``simulate_flood`` function for one
    event duration.
    """
    if len(event_times_s) == 0:
        raise ValueError("event_times_s must contain at least one time")
    if any(event_time_s < 0 for event_time_s in event_times_s):
        raise ValueError("event times must be non-negative")

    return tuple(
        simulate_flood(
            breach,
            discharge,
            event_time_s,
            spatial_data,
            area_map,
        )
        for event_time_s in event_times_s
    )


def print_flood_indicators(
    depths_m: Sequence[np.ndarray],
    event_times_s: Sequence[float],
    spatial_data: SpatialData,
    area_map: AreaMap,
) -> None:
    """Print depth, water-level, and volume indicators for each time step."""
    if len(depths_m) != len(event_times_s):
        raise ValueError("depths_m and event_times_s must have equal lengths")

    print("Flood indicators")
    print("=" * 72)
    for depth_grid, event_time_s in zip(depths_m, event_times_s):
        finite_depths = depth_grid[np.isfinite(depth_grid)]
        flooded_depths = finite_depths[finite_depths > 0]
        total_volume_m3 = float(np.sum(np.maximum(finite_depths, 0.0)) * CELL_AREA_M2)
        max_depth_m = float(np.max(flooded_depths)) if flooded_depths.size else 0.0
        flooded_cells = int(np.count_nonzero(finite_depths > 0))

        print(f"\nTime: {event_time_s / 3600:.2f} h")
        print(f"  Total water volume: {total_volume_m3:,.0f} m3")
        print(f"  Flooded cells: {flooded_cells:,}")
        print(f"  Maximum depth: {max_depth_m:.2f} m")
        print("  Compartments:")
        for compartment_id in sorted(area_map.compartments):
            coordinates = area_map.compartments[compartment_id]
            if not coordinates:
                continue
            cell_indices = tuple(zip(*coordinates))
            compartment_depths = depth_grid[cell_indices]
            ground_elevations = spatial_data.average_elevation[cell_indices]
            flooded = np.isfinite(compartment_depths) & (compartment_depths > 0)
            average_depth_m = (
                float(np.mean(compartment_depths[flooded])) if np.any(flooded) else 0.0
            )
            water_surface_m = compartment_depths[flooded] + ground_elevations[flooded]
            average_surface_m = (
                float(np.mean(water_surface_m)) if water_surface_m.size else 0.0
            )
            print(
                f"    {compartment_id}: "
                f"avg depth {average_depth_m:.2f} m, "
                f"avg water level {average_surface_m:.2f} m, "
                f"flooded cells {int(np.count_nonzero(flooded)):,}"
            )


def plot_flood_progression(
    water_levels: Sequence[np.ndarray],
    event_times_s: Sequence[float],
    *,
    area_map: AreaMap | None = None,
    interval_ms: int = 800,
):
    """Create a Matplotlib animation of water depths across the cell grid.

    The function returns ``(figure, animation)`` and does not call
    ``matplotlib.pyplot.show()``. Call ``plt.show()`` in a notebook or script,
    or save the returned animation with Matplotlib's animation writers.
    """
    if len(water_levels) == 0:
        raise ValueError("water_levels must contain at least one array")
    if len(water_levels) != len(event_times_s):
        raise ValueError("water_levels and event_times_s must have equal lengths")
    if interval_ms <= 0:
        raise ValueError("interval_ms must be positive")

    import matplotlib.pyplot as plt
    from matplotlib.animation import FuncAnimation

    first_levels = water_levels[0]
    height, width = first_levels.shape
    figure, axis = plt.subplots(figsize=(11, 6))
    image = axis.imshow(
        first_levels,
        origin="upper",
        cmap="Blues",
        interpolation="nearest",
        extent=(0, width * 100.0, height * 100.0, 0),
        vmin=0.0,
        vmax=10.0,
    )
    if area_map is not None:
        for compartment_id, coordinates in area_map.compartments.items():
            if not coordinates:
                continue
            y_coordinates, x_coordinates = zip(*coordinates)
            axis.text(
                float(np.mean(x_coordinates)) * 100.0,
                float(np.mean(y_coordinates)) * 100.0,
                str(compartment_id),
                color="black",
                fontsize=14,
                fontweight="bold",
                ha="center",
                va="center",
                bbox={
                    "facecolor": "white",
                    "alpha": 0.7,
                    "edgecolor": "none",
                },
            )
    colorbar = figure.colorbar(image, ax=axis)
    colorbar.set_label("Water depth [m]")
    axis.set_xlabel("x [m]")
    axis.set_ylabel("y [m]")
    title = axis.set_title("")

    def update(frame_index: int):
        levels_m = water_levels[frame_index]
        image.set_data(levels_m)
        title.set_text(f"Flood progression: {event_times_s[frame_index] / 3600:.1f} h")
        return image, title

    animation = FuncAnimation(
        figure,
        update,
        frames=len(water_levels),
        interval=interval_ms,
        blit=False,
        repeat=False,
    )
    return figure, animation