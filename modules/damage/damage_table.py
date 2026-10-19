"""
Damage & Casualty Table Generator.
"""

import pandas as pd
import numpy as np

from .damage_calculator import (
    RISE_RATE_M_PER_S,
    RISE_RATE_M_PER_HOUR,
    casualty_factor_vectorized,
    calculate_land_use_damage_vectorized,
    calculate_vehicle_damage_vectorized,
)


def create_damage_table(inundation_table: pd.DataFrame) -> pd.DataFrame:
    """
    Process inundation maps across all return periods to compute total economic 
    damage (€) and total casualties, excluding all NaN values.

    Parameters
    ----------
    inundation_table : pd.DataFrame
        DataFrame containing columns: ['return period [years]', 'map'].
        Each nested 'map' DataFrame contains ['land use type', 'population', 'water depth'].

    Returns
    -------
    pd.DataFrame
        Summary table containing:
        ['return period [years]', 'total damage [euros]', 'total casualties']
    """
    # Verify rate conversion constant availability
    _ = RISE_RATE_M_PER_S

    results = []

    for _, row in inundation_table.iterrows():
        rp = row["return period [years]"]
        cell_df: pd.DataFrame = row["map"]

        # Strictly exclude all NaN rows across required columns
        clean_df = cell_df.dropna(subset=["land use type", "population", "water depth"]).copy()

        depths = clean_df["water depth"].to_numpy()
        land_uses = clean_df["land use type"].to_numpy()
        populations = clean_df["population"].to_numpy()

        # Vectorized calculations
        land_use_damage = calculate_land_use_damage_vectorized(depths, land_uses)
        vehicle_damage = calculate_vehicle_damage_vectorized(depths, populations)
        total_cell_damage = land_use_damage + vehicle_damage

        c_factors = casualty_factor_vectorized(
            depths, rise_rate_m_hr=RISE_RATE_M_PER_HOUR, velocity=0.0
        )
        cell_casualties = c_factors * np.maximum(0.0, populations)

        total_damage_eur = float(np.sum(total_cell_damage))
        total_casualties = float(np.sum(cell_casualties))

        results.append({
            "return period [years]": rp,
            "total damage [euros]": total_damage_eur,
            "total casualties": total_casualties,
        })

    return pd.DataFrame(results)