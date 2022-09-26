from typing import List

from abmbiopsy.sample import Sample


class SampleNeedle(Sample):
    """
    Representation of a simulated sample in needle shape.

    The needle samples represent fine-needle aspiration biopsies, which
    use a hollow needle to remove a tissue sample.

    Attributes
    ----------
    simulation_radius : int
        Radius of the simulation.
    sample_width : int
        Width of the sample.
    """

    sample_shape = "needle"
    """string: Shape of the sample."""

    def __init__(self, simulation_radius: int, sample_width: int):
        self.simulation_radius = simulation_radius
        self.sample_width = sample_width

    def select_sample_locations(self) -> List[tuple]:
        """
        Get a list of needle sampling locations.

        Returns
        -------
        :
            Coordinates for needle sample locations.
        """
        if (self.sample_width % 2) == 0:
            raise ValueError("Width has to be an even number.")

        half_width = (self.sample_width + 1) / 2

        return [
            (u, v, w)
            for u in range(-self.simulation_radius + 1, self.simulation_radius)
            for v in range(-self.simulation_radius + 1, self.simulation_radius)
            for w in range(-self.simulation_radius + 1, self.simulation_radius)
            if (u + v + w) == 0 and abs(u) < half_width and v <= 0 and w >= 0
        ]
