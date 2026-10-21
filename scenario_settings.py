"""Available model scenarios."""

from dataclasses import dataclass, field
from enum import Enum

from dike_settings import DIKE16, DIKE43, DIKE16_WIDE, DIKE43_WIDE, DikeSettings
from modules.inundation.compartment_data import COMPARTMENT_BORDERS
from modules.inundation.inundation_settings import COMPARTMENT_BORDERS_RAISED


class ScenarioType(Enum):
    BASELINE = "baseline"
    WIDE_RIVER_DIKE43 = "wide_river_dike43"
    WIDE_RIVER_DIKE16 = "wide_river_dike16"
    BERM_DIKE16 = "berm_dike16"
    DRAINAGE_DIKE16 = "drainage_dike16"
    BERM_DIKE43 = "berm_dike43"
    DRAINAGE_DIKE43 = "drainage_dike43"
    RAISED_COMPARTMENT_BORDERS = "raised_compartment_borders"


class DikeType(Enum):
    DIKE16 = "DIKE16"
    DIKE43 = "DIKE43"


@dataclass(frozen=True)
class Scenario:
    type: ScenarioType
    dike16: DikeSettings = field(default_factory=lambda: DIKE16)
    dike43: DikeSettings = field(default_factory=lambda: DIKE43)
    compartment_borders: dict[tuple[int, int], float] = field(
        default_factory=lambda: COMPARTMENT_BORDERS
    )

    def dike(self, dike_type: DikeType) -> DikeSettings:
        if dike_type is DikeType.DIKE16:
            return self.dike16
        if dike_type is DikeType.DIKE43:
            return self.dike43

SCENARIOS: list[Scenario] = [
    Scenario(ScenarioType.BASELINE),
    Scenario(
        ScenarioType.WIDE_RIVER_DIKE43,
        dike43=DIKE43_WIDE,
    ),
    Scenario(
        ScenarioType.WIDE_RIVER_DIKE16,
        dike16=DIKE16_WIDE,
    ),
    Scenario(ScenarioType.BERM_DIKE16),
    Scenario(ScenarioType.DRAINAGE_DIKE16),
    Scenario(ScenarioType.BERM_DIKE43),
    Scenario(ScenarioType.DRAINAGE_DIKE43),
    Scenario(
        ScenarioType.RAISED_COMPARTMENT_BORDERS,
        compartment_borders=COMPARTMENT_BORDERS_RAISED,
    ),
]
