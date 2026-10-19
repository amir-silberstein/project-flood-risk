import math

from breach.breach_settings import (
    BREACH_TIME_STEP,
    BREACH_DEVELOPMENT_TIME,
    BREACH_SIMULATION_DURATION,
    BREACH_INITIAL_WIDTH,
    BREACH_MAXIMUM_WIDTH,
    BREACH_MAXIMUM_GROWTH_RATE,
    BREACH_GRAVITY,
    BREACH_CRITICAL_VELOCITY,
    BREACH_FACTOR_1,
    BREACH_FACTOR_2,
    BREACH_DOWNSTREAM_HEAD_RATIO,
    BREACH_DISCHARGE_COEFFICIENT,
)


def calculate_breach_discharge(
    water_level_nap: float,
    crest_height_nap: float,
    floodplains_bed_nap: float,
) -> float:
    """Calculate breach discharge for a given water level in NAP."""

    breach_width = BREACH_INITIAL_WIDTH
    breach_discharge = 0.0
    num_steps = int(BREACH_SIMULATION_DURATION / BREACH_TIME_STEP) + 1

    for step in range(num_steps):
        time = step * BREACH_TIME_STEP

        if time <= BREACH_DEVELOPMENT_TIME:
            bed_level = crest_height_nap - (
                crest_height_nap - floodplains_bed_nap
            ) * (time / BREACH_DEVELOPMENT_TIME)
            width_growth_rate = 0.0

        else:
            bed_level = floodplains_bed_nap
            upstream_head = max(0.0, water_level_nap - bed_level)

            if upstream_head > 0:
                downstream_head = (
                    BREACH_DOWNSTREAM_HEAD_RATIO * upstream_head
                )
                head_difference = upstream_head - downstream_head
                elapsed_growth_time = time - BREACH_DEVELOPMENT_TIME

                numerator = (
                    BREACH_FACTOR_1
                    * BREACH_FACTOR_2
                    * (BREACH_GRAVITY * head_difference) ** 1.5
                )
                denominator = (
                    math.log(10)
                    * BREACH_CRITICAL_VELOCITY**2
                    * (
                        1
                        + (
                            BREACH_FACTOR_2
                            * BREACH_GRAVITY
                            / BREACH_CRITICAL_VELOCITY
                        )
                        * elapsed_growth_time
                    )
                )

                width_growth_rate = min(
                    numerator / denominator,
                    BREACH_MAXIMUM_GROWTH_RATE,
                )
            else:
                width_growth_rate = 0.0

        upstream_head = max(0.0, water_level_nap - bed_level)

        breach_discharge = (
            (2 / 3) ** 1.5
            * math.sqrt(BREACH_GRAVITY)
            * breach_width
            * upstream_head**1.5
            * BREACH_DISCHARGE_COEFFICIENT
        )

        if breach_width >= BREACH_MAXIMUM_WIDTH:
            break

        breach_width = min(
            breach_width + width_growth_rate * BREACH_TIME_STEP,
            BREACH_MAXIMUM_WIDTH,
        )

    return breach_discharge