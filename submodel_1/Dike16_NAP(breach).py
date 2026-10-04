"""Dike 16 breach-model entry point."""

from submodel_1.Dike16_NAP import calculate_water_level
from submodel_1.breach import BreachParameters
from submodel_1.breach import simulate_breach as _simulate_breach

PARAMETERS = BreachParameters(
    floodplain_bed_nap=2.45,
    crest_height_nap=7.88,
    duration=3600.0,
)


def simulate_breach(
    water_level_NAP: float,
    t_end: float | None = None,
    dt: float | None = None,
    B_initial: float | None = None,
    print_steps: bool = True,
):
    """Simulate Dike 16 breach growth and discharge."""
    parameters = PARAMETERS
    if dt is not None or B_initial is not None:
        parameters = BreachParameters(
            **{
                **parameters.__dict__,
                "dt": parameters.dt if dt is None else dt,
                "initial_width": parameters.initial_width if B_initial is None else B_initial,
            }
        )
    return _simulate_breach(
        water_level_NAP,
        parameters,
        t_end=t_end,
        print_steps=print_steps,
    )


if __name__ == "__main__":
    _, water_level_nap, _ = calculate_water_level(15270, show_output=False)
    simulate_breach(water_level_nap)
