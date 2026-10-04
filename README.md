# Flood Risk Model

Run commands from the project root.

## Submodel 1

Submodel 1 calculates water levels for Dike 16 and Dike 43.

```bash
python -m submodel_1.run_stage1
```

Build the connected scenario table and write `Scenario_Probabilities.csv`:

```bash
python -m submodel_1.Flood_scenario_table_Dikes_16_and_43
```

Run a breach example directly:

```bash
python 'submodel_1/Dike16_NAP(breach).py'
python 'submodel_1/Dike43_NAP(breach).py'
```

The main callable functions are `calculate_water_level(...)` for a dike level and `simulate_breach(...)` for breach growth and discharge.

## Submodel 3

Run the complete flood-propagation, damage, casualty, and visualization example:

```bash
python -m submodel_3.run_vis
```

The example loads the raster data from `spatial_data_dike_ring_area/`, simulates flood depths, calculates economic and vehicle damage, prints casualty estimates, and opens the flood animation.

For programmatic use, the main functions are:

```python
from submodel_3.spatial_areas import create_area_map, load_spatial_data
from submodel_3.flood import simulate_flood
from submodel_3.damage import (
    calculate_flood_damage,
    cells_from_flood,
    print_damage_summary,
)

spatial_data = load_spatial_data()
area_map = create_area_map(spatial_data)
breach = area_map.compartments[1][0]
depths = simulate_flood(breach, 16000.0, 24 * 3600, spatial_data, area_map)
cells = cells_from_flood(depths, spatial_data, area_map)
calculate_flood_damage(cells)
print_damage_summary(cells)
```

Install the required packages in the active Python environment if needed:

```bash
python -m pip install numpy scipy pandas matplotlib pytest
```
