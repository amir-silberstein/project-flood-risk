from scipy.optimize import fsolve

from dike_settings import DikeSettings


def calculate_water_level(
    discharge_lobith: float,
    manning_main_channel: float,
    manning_floodplains: float,
    dike: DikeSettings,
) -> float:
    """Calculate water level in m NAP for a given discharge and dike."""

    discharge: float = discharge_lobith * dike.discharge_fraction

    floodplains_threshold: float = (
        dike.floodplains_bed_nap - dike.river_bed_nap
    )

    water_depth_guess: float = (
        discharge
        / (
            dike.main_channel_width
            * (dike.river_slope**0.5 / manning_main_channel)
        )
    ) ** (3 / 5)

    if water_depth_guess <= floodplains_threshold:
        water_depth: float = water_depth_guess

    else:

        def discharge_balance(water_depth: float) -> float:
            floodplains_depth: float = (
                water_depth - floodplains_threshold
            )

            main_channel_area: float = (
                dike.main_channel_width * water_depth
            )
            floodplains_area: float = (
                dike.floodplains_width * floodplains_depth
            )

            main_channel_velocity: float = (
                water_depth ** (2 / 3)
                * dike.river_slope**0.5
                / manning_main_channel
            )
            floodplains_velocity: float = (
                floodplains_depth ** (2 / 3)
                * dike.river_slope**0.5
                / manning_floodplains
            )

            calculated_discharge: float = (
                main_channel_area * main_channel_velocity
                + floodplains_area * floodplains_velocity
            )

            return calculated_discharge - discharge

        water_depth = float(
            fsolve(discharge_balance, water_depth_guess)[0]
        )

    return round(water_depth + dike.river_bed_nap, 2)