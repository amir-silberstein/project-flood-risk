"""Static configuration for the six flood compartments."""

from types import MappingProxyType
from typing import Final

COMPARTMENT_IDS: Final[tuple[int, ...]] = (1, 2, 3, 4, 5, 6)

# Absolute water-surface elevations at the compartment borders [m].
COMPARTMENT_BORDERS: Final[dict[tuple[int, int], float]] = {
    (1, 2): 15.0,
    (2, 3): 8.0,
    (3, 4): 10.0,
    (3, 5): 10.0,
    (4, 6): 5.0,
    (5, 6): 5.0,
}

# Directed spill connections. A connection is traversed after its border level
# is reached; the reverse direction is not a spill path.
COMPARTMENT_CONNECTIONS: Final[dict[int, tuple[int, ...]]] = {
    1: (2,),
    2: (3,),
    3: (4, 5),
    4: (6,),
    5: (6,),
    6: (),
}

# Read-only views for callers that should not mutate model configuration.
COMPARTMENTS: Final = MappingProxyType(
    {compartment_id: compartment_id for compartment_id in COMPARTMENT_IDS}
)
BORDERS: Final = MappingProxyType(COMPARTMENT_BORDERS)
CONNECTIONS: Final = MappingProxyType(COMPARTMENT_CONNECTIONS)
