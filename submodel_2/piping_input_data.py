"""Piping inputs for the assigned Set 4 cross-sections."""

from submodel_2.piping import PipingParameters


# Selected coordinates from set4_16_Vianen_VY063_117m-1.pdf and
# set4_43_Bemmel_DD123_000m-1.pdf (upper DD123 profile).
# Hydraulic entry/exit choices are assumptions, not measured flow paths.
# Ground-level exit heads assume no standing water at the exit.
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

# Vianen cover: DIke_16_4.stix, soil boundaries at x = 25.04 m.
# Bemmel: zero means no cover credit, not an absent cover layer.
# Dike_43_4.stix matches DD124; its cover is not transferred to DD123.
# C limits: BEP_H_Cheng_UT-1.pdf, slide 30; uniformity is our assumption.
# Bligh: lecture slide 27; correction: TRSandBoilsPiping.pdf, sec. 4.2.2, Eq. 7.
# The Monte Carlo lecture permits choosing an uncertainty distribution.
LONGER_SEEPAGE_LENGTHS = {16: 25.04 - (-18.63), 43: 18.92 - (-25.10)}
SAMPLE_SIZE = 200000
RANDOM_SEEDS = {16: 20261003, 43: 20261004}
