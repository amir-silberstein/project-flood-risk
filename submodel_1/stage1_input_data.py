"""Input data for the stage-1 hydraulic model."""

from submodel_1.stage1_hydraulic import HydraulicParameters


DIKE_16_PARAMETERS = HydraulicParameters(
    river_bed_nap=-3.8,
    floodplain_bed_nap=2.45,
    crest_height_nap=7.88,
    main_channel_height=6.25,
    discharge_fraction=2 / 9,
    river_slope=0.00011,
    manning_main_channel=0.03,
    manning_floodplain=0.05,
    main_channel_width=155,
    total_channel_width=500,
)

DIKE_43_PARAMETERS = HydraulicParameters(
    river_bed_nap=2.55,
    floodplain_bed_nap=9.75,
    crest_height_nap=16.62,
    main_channel_height=7.2,
    discharge_fraction=2 / 3,
    river_slope=0.00016,
    manning_main_channel=0.03,
    manning_floodplain=0.05,
    main_channel_width=270,
    total_channel_width=680,
)

RETURN_PERIODS = (5, 10, 50, 100, 250, 500, 1250, 4000, 10000, 100000)

DISCHARGES_LOBITH = (7970, 9140, 11890, 12940, 14380, 15270, 16560, 18190, 19480, 22710)

UNCERTAINTY_BANDS = (1725, 1999, 2862, 3175, 2979, 3567, 4547, 5919, 7095, 10114)
