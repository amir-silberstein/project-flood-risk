import numpy as np

# Hardcoded Rise Rate: 15 cm/hour converted to meters/second
RISE_RATE_CM_PER_HOUR: float = 15.0
RISE_RATE_M_PER_S: float = (RISE_RATE_CM_PER_HOUR / 100.0) / 3600.0  # 4.1667e-5 m/s
RISE_RATE_M_PER_HOUR: float = RISE_RATE_CM_PER_HOUR / 100.0        # 0.15 m/hr


def casualty_factor_vectorized(
    depth: np.ndarray,
    rise_rate_m_hr: float = RISE_RATE_M_PER_HOUR,
    velocity: float = 0.0,
) -> np.ndarray:
    """
    Calculate the Dutch Standard Method fatality factor for arrays of water depth.
    
    Parameters
    ----------
    depth : np.ndarray
        Array of water depth values (meters).
    rise_rate_m_hr : float
        Rise rate in meters/hour (default is 0.15 m/hr = 15 cm/hr).
    velocity : float
        Flow velocity in m/s (default 0.0 m/s).

    Returns
    -------
    np.ndarray
        Fatality factors clipped between 0.0 and 1.0.
    """
    factors = np.zeros_like(depth, dtype=float)
    valid_mask = np.isfinite(depth) & (depth > 0)

    if not np.any(valid_mask):
        return factors

    d = depth[valid_mask]

    # Dutch Standard Method conditions
    high_hazard = (d * velocity >= 7.0) & (velocity >= 2.0)
    
    if rise_rate_m_hr >= 0.5:
        c1 = high_hazard
        c2 = ~high_hazard & (d > 4.7)
        c3 = ~high_hazard & (d >= 1.5) & (d <= 4.7)
        c4 = ~high_hazard & (d < 1.5)

        sub_factors = np.zeros_like(d)
        sub_factors[c1 | c2] = 1.0
        sub_factors[c3] = 1.45e-3 * np.exp(1.39 * d[c3])
        sub_factors[c4] = 1.34e-3 * np.exp(0.59 * d[c4])
    else:
        sub_factors = np.where(high_hazard, 1.0, 1.34e-3 * np.exp(0.59 * d))

    factors[valid_mask] = np.clip(sub_factors, 0.0, 1.0)
    return factors


def _single_family_fraction_vec(depth: np.ndarray) -> np.ndarray:
    frac = np.zeros_like(depth)
    m1 = (depth > 0) & (depth <= 1.0)
    m2 = (depth > 1.0) & (depth <= 2.0)
    m3 = (depth > 2.0) & (depth <= 4.0)
    m4 = (depth > 4.0) & (depth <= 5.0)
    m5 = depth > 5.0

    d1, d2, d3, d4 = depth[m1], depth[m2], depth[m3], depth[m4]

    frac[m1] = -0.14897 * d1**2 + 0.32872 * d1
    frac[m2] = 0.00342 * d2**2 + 0.04024 * d2 + 0.13946
    frac[m3] = 0.03232 * d3**2 + 0.05303 * d3 - 0.00168
    frac[m4] = -0.27246 * d4**2 + 2.72460 * d4 - 5.81189
    frac[m5] = 1.0

    return np.clip(frac, 0.0, 1.0)


def _multi_family_fraction_vec(depth: np.ndarray) -> np.ndarray:
    frac = np.zeros_like(depth)
    m1 = (depth > 0) & (depth <= 6.0)
    m2 = depth > 6.0

    frac[m1] = 1.0 - (1.0 - depth[m1] / 6.0) ** 4
    frac[m2] = 1.0

    return np.clip(frac, 0.0, 1.0)


def _depth_curve_vec(depth: np.ndarray) -> np.ndarray:
    c1 = depth
    c2 = 0.24 * depth + 0.4
    c3 = 0.07 * depth + 0.75
    return np.clip(np.minimum(c1, np.minimum(c2, c3)), 0.0, 1.0)


def _employee_damage_vec(depth: np.ndarray, employees: float, max_damage: float) -> np.ndarray:
    frac = np.zeros_like(depth)
    m1 = (depth > 0) & (depth <= 1.0)
    m2 = (depth > 1.0) & (depth <= 3.0)
    m3 = (depth > 3.0) & (depth <= 5.0)
    m4 = depth > 5.0

    frac[m1] = 0.1 * depth[m1]
    frac[m2] = 0.06 * depth[m2] + 0.04
    frac[m3] = 0.39 * depth[m3] - 0.95
    frac[m4] = 1.0

    return frac * max_damage * employees


def calculate_land_use_damage_vectorized(
    depth: np.ndarray, land_use: np.ndarray
) -> np.ndarray:
    """Calculate land use economic damage (€) for vectorized cell arrays."""
    sf_val, mf_val = 241000.0, 172000.0
    damage = np.zeros_like(depth, dtype=float)

    valid = np.isfinite(depth) & (depth > 0) & np.isfinite(land_use)
    if not np.any(valid):
        return damage

    d = depth
    lu = land_use.astype(int)

    # Class 1: Infrastructure
    m1 = valid & (lu == 1)
    if np.any(m1):
        frac1 = np.minimum(d[m1], np.minimum(0.28, np.minimum(0.18 * d[m1] + 0.1, 1.0)))
        damage[m1] = frac1 * 13668.0 * 150.0

    # Class 2: Residential
    m2 = valid & (lu == 2)
    if np.any(m2):
        sf_frac = _single_family_fraction_vec(d[m2])
        mf_frac = _multi_family_fraction_vec(d[m2])
        damage[m2] = 20.2 * (0.64 * sf_val * sf_frac + 0.36 * mf_val * mf_frac)

    # Class 3: Industry / Commercial
    m3 = valid & (lu == 3)
    if np.any(m3):
        damage[m3] = _employee_damage_vec(d[m3], employees=56.0, max_damage=537416.67)

    # Class 4: Government / Services
    m4 = valid & (lu == 4)
    if np.any(m4):
        damage[m4] = _employee_damage_vec(d[m4], employees=56.0, max_damage=16850.0)

    # Class 5: Recreation
    m5 = valid & (lu == 5)
    if np.any(m5):
        damage[m5] = _depth_curve_vec(d[m5]) * 109000.0

    # Class 6: Greenhouses
    m6 = valid & (lu == 6)
    if np.any(m6):
        damage[m6] = _depth_curve_vec(d[m6]) * 441000.0

    # Class 7: Agriculture
    m7 = valid & (lu == 7)
    if np.any(m7):
        damage[m7] = _depth_curve_vec(d[m7]) * 31000.0

    # Class 8 & 9: Water & Nature (0.0 damage)
    return damage


def calculate_vehicle_damage_vectorized(
    depth: np.ndarray, population: np.ndarray
) -> np.ndarray:
    """Calculate vehicle economic damage (€) for vectorized cell arrays."""
    damage = np.zeros_like(depth, dtype=float)
    valid = np.isfinite(depth) & (depth > 0) & np.isfinite(population) & (population > 0)

    if not np.any(valid):
        return damage

    d = depth[valid]
    pop = population[valid]

    f1 = np.abs(0.17 * d - 0.03)
    f2 = np.abs(0.72 * d - 0.3)
    f3 = np.abs(0.31 * d + 0.1)
    frac = np.clip(np.minimum(f1, np.minimum(f2, f3)), 0.0, 1.0)

    damage[valid] = 0.48 * pop * frac * 1070.0
    return damage