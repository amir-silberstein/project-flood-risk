from global_settings import FLOOD_DURATION

# Manning Roughness Defaults
MANNING_MAIN_CHANNEL: float = 0.03
MANNING_FLOODPLAINS: float = 0.05

# Manning Roughness Variations: [min, max]
MANNING_MAIN_CHANNEL_VARIATIONS: list[float] = [0.022, 0.06]
MANNING_FLOODPLAINS_VARIATIONS: list[float] = [0.035, 0.15]

# Breach Simulation Settings
BREACH_TIME_STEP: float = 10.0  # seconds
BREACH_DEVELOPMENT_TIME: float = 600.0  # seconds
BREACH_SIMULATION_DURATION: float = FLOOD_DURATION * 3600.0  # seconds

# Breach Width
BREACH_INITIAL_WIDTH: float = 20.0  # meters
BREACH_MAXIMUM_WIDTH: float = 100.0  # meters
BREACH_MAXIMUM_GROWTH_RATE: float = 1.0  # m/s

# Breach Hydraulic Parameters
BREACH_GRAVITY: float = 10.0  # m/s^2
BREACH_CRITICAL_VELOCITY: float = 0.2  # m/s
BREACH_FACTOR_1: float = 1.2
BREACH_FACTOR_2: float = 0.04
BREACH_DOWNSTREAM_HEAD_RATIO: float = 2 / 3  # Ratio of downstream to upstream head
BREACH_DISCHARGE_COEFFICIENT: float = 1.0


