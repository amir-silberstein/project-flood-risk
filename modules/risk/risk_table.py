"""Risk table calculation."""

import pandas as pd

from .risk import calculate_risk


RETURN_PERIOD_COLUMN = "return period [years]"
OCCURRENCE_PROBABILITY_COLUMN = "probability"
DIKE_FAILURE_PROBABILITY_COLUMN = "probability of dike failure"
DAMAGE_COLUMN = "total damage [euros]"
CASUALTIES_COLUMN = "total casualties"


def create_risk_table(
    hydrological_table: pd.DataFrame,
    dike_failure_table: pd.DataFrame,
    damage_table: pd.DataFrame,
) -> pd.DataFrame:
    """Create event probability, damage risk, and casualty risk by return period."""

    combined_table = hydrological_table[
        [RETURN_PERIOD_COLUMN, OCCURRENCE_PROBABILITY_COLUMN]
    ].merge(
        dike_failure_table[
            [RETURN_PERIOD_COLUMN, DIKE_FAILURE_PROBABILITY_COLUMN]
        ],
        on=RETURN_PERIOD_COLUMN,
    ).merge(
        damage_table[[RETURN_PERIOD_COLUMN, DAMAGE_COLUMN, CASUALTIES_COLUMN]],
        on=RETURN_PERIOD_COLUMN,
    )

    results = [
        calculate_risk(
            row[DIKE_FAILURE_PROBABILITY_COLUMN],
            row[OCCURRENCE_PROBABILITY_COLUMN],
            row[DAMAGE_COLUMN],
            row[CASUALTIES_COLUMN],
        )
        for _, row in combined_table.iterrows()
    ]

    return pd.DataFrame(
        {
            RETURN_PERIOD_COLUMN: combined_table[RETURN_PERIOD_COLUMN],
            "event probability": [result.event_probability for result in results],
            "risk damage [euros]": [result.risk_damage for result in results],
            "risk casualties": [result.risk_casualties for result in results],
        }
    )
