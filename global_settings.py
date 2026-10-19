RETURN_PERIODS: list[float] = [  # Years
    12.5,
    125,
    1250,
    12500,
    125000,
]

Q_LOBITH_BASELINE: list[float] = [  # m^3/s
    9738.657,
    13634.48,
    17474.07,
    21308.24,
    25141.87,
]

Q_LOBITH_CLIMATE_CHANGE: list[float] = [  # m^3/s
    q * 1.4 for q in Q_LOBITH_BASELINE
]

FLOOD_DURATION: float = 24 * 5  # hours

