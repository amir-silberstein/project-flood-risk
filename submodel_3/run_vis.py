import numpy as np
import matplotlib.pyplot as plt

from submodel_3.spatial_areas import load_spatial_data, create_area_map
from submodel_3.damage import (
    calculate_flood_damage,
    cells_from_flood,
    print_damage_summary,
)
from submodel_3.visualization import (
    calculate_flood_progression,
    plot_flood_progression,
    print_flood_indicators,
)

spatial_data = load_spatial_data()
area_map = create_area_map(spatial_data)

# Choose a valid cell from compartment 1
breach = area_map.compartments[1][0]

event_times_s = np.linspace(0, 24*3600, 5)
depths = calculate_flood_progression(
    breach=breach,
    discharge=16000.0,  # Replace with the hydraulic-model discharge
    event_times_s=event_times_s,
    spatial_data=spatial_data,
    area_map=area_map,
)

# Damage uses only the final depth grid, after flood propagation is complete.
final_cells = cells_from_flood(depths[-1], spatial_data, area_map)
calculate_flood_damage(final_cells)
print_damage_summary(final_cells)

print_flood_indicators(depths, event_times_s, spatial_data, area_map)

figure, animation = plot_flood_progression(
    depths,
    event_times_s,
    area_map=area_map,
)

plt.show()