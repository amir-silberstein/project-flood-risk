# Manning Roughness Defaults
MANNING_MAIN_CHANNEL: float = 0.03
MANNING_FLOODPLAINS: float = 0.05

# Manning Roughness Variations: [min, max]
MANNING_MAIN_CHANNEL_VARIATIONS: list[float] = [0.022, 0.06]
MANNING_FLOODPLAINS_VARIATIONS: list[float] = [0.035, 0.15]

# Dike 16:
DIKE16_RIVER_BED_NAP: float = -3.8 # meters
DIKE16_FLOODPLAINS_BED_NAP: float = 2.45 # meters
DIKE16_MAIN_CHANNEL_WIDTH: float = 155 # meters
DIKE16_FLOODPLAINS_WIDTH: float = 500 # meters
DIKE16_DISCHARGE_FRACTION: float = 2 / 9  # Fraction of discharge that goes through the main channel


# Dike 43:
DIKE43_RIVER_BED_NAP: float = 2.55 # meters
DIKE43_FLOODPLAINS_BED_NAP: float = 9.75 # meters
DIKE43_MAIN_CHANNEL_WIDTH: float = 270 # meters
DIKE43_FLOODPLAINS_WIDTH: float = 680 # meters
DIKE43_DISCHARGE_FRACTION: float = 2 / 3  # Fraction of discharge that goes through the main channel


