from dataclasses import dataclass, replace

@dataclass
class DikeSettings:
    """Physical and hydraulic properties of a dike."""

    crest_height_nap: float  # meters
    river_bed_nap: float  # meters
    floodplains_bed_nap: float  # meters
    main_channel_width: float  # meters
    floodplains_width: float  # meters
    discharge_fraction: float  # Fraction flowing through the main channel
    river_slope: float
    compartment_id: int

DIKE16: DikeSettings = DikeSettings(
    crest_height_nap=7.88,
    river_bed_nap=-3.8,
    floodplains_bed_nap=2.45,
    main_channel_width=155,
    floodplains_width=500,
    discharge_fraction=2 / 9,
    river_slope=0.00011,
    compartment_id=1,
)

DIKE16_WIDE: DikeSettings = replace(
    DIKE16,
    main_channel_width=DIKE16.main_channel_width + 50,
)

DIKE43: DikeSettings = DikeSettings(
    crest_height_nap=16.62,
    river_bed_nap=2.55,
    floodplains_bed_nap=9.75,
    main_channel_width=270,
    floodplains_width=680,
    discharge_fraction=2 / 3,
    river_slope=0.00016,
    compartment_id=6,
)

DIKE43_WIDE: DikeSettings = replace(
    DIKE43,
    main_channel_width=DIKE43.main_channel_width + 50,
)