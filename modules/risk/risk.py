"""Calculations for expected flood damage and casualties."""

from typing import NamedTuple


class RiskResult(NamedTuple):
    """Risk results for one flood scenario."""

    event_probability: float
    risk_damage: float
    risk_casualties: float


def calculate_risk(
    probability_of_dike_failure: float,
    probability_of_flood_occurrence: float,
    total_damage_euros: float,
    casualties: float,
) -> RiskResult:
    """Return event probability, expected damage, and expected casualties."""

    event_probability: float = (
        probability_of_dike_failure * probability_of_flood_occurrence
    )
    risk_damage: float = event_probability * total_damage_euros
    risk_casualties: float = event_probability * casualties

    return RiskResult(
        event_probability=event_probability,
        risk_damage=risk_damage,
        risk_casualties=risk_casualties,
    )
