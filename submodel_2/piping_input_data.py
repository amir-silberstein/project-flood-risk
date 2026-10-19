"""Piping inputs for the assigned Set 4 cross-sections."""

from submodel_2.piping import PipingParameters


DIKE_16_PARAMETERS = PipingParameters(
    seepage_length=25.04 - (-9.56),
    exit_head_nap=2.02,
    cover_thickness=5.163196261682243,
    crest_height_nap=7.88,
)

DIKE_43_PARAMETERS = PipingParameters(
    seepage_length=18.92 - (-13.50),
    exit_head_nap=11.62,
    cover_thickness=0.0,
    crest_height_nap=16.62,
)
LONGER_SEEPAGE_LENGTHS = {16: 25.04 - (-18.63), 43: 18.92 - (-25.10)}
SAMPLE_SIZE = 200000
RANDOM_SEEDS = {16: 20261003, 43: 20261004}
