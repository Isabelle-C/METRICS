from typing import List, Union

from abmbiopsy.sample import Sample


class SampleNeedle(Sample):
    """
    Representation of a simulated sample in needle shape.

    The needle samples represent fine-needle aspiration biopsies, which
    use a hollow needle to remove a tissue sample.

    Attributes
    ----------
    simulation_radius :
        Radius of the simulation.
    sample_width :
        Width of the sample.
    direction : {1,2,3,4,5,6}
        Direction of the sample.
    """

    def __init__(self, simulation_radius: int, sample_width: int, direction: int):
        self.simulation_radius = simulation_radius
        self.sample_width = sample_width
        self.direction = direction

    def get_sample_key(self) -> str:
        """
        Get key that describes sample method.

        Returns
        -------
        :
            Sample key which includes sampling method, simulation radius, and sample width.
        """
        return f"needle-R{self.simulation_radius}-W{self.sample_width}-D{self.direction}"

    def select_sample_locations(self) -> List[tuple]:
        """
        Get a list of needle sampling locations.

        Returns
        -------
        :
            Coordinates for needle sample locations.
        """
        if (self.sample_width % 2) == 0:
            raise ValueError("Width has to be an odd number.")

        half_width = (self.sample_width + 1) / 2

        coord_range = range(-self.simulation_radius + 1, self.simulation_radius)
        return [
            (u, v, w)
            for u in coord_range
            for v in coord_range
            for w in coord_range
            if self.valid_coords_for_needle_direction((u, v, w), self.direction, half_width)
        ]

    @staticmethod
    def valid_coords_for_needle_direction(
        coords: tuple, direction: int, half_width: Union[int, float]
    ) -> bool:
        """
        Parameters
        ----------
        coords :
            Sample coordinate u, v, and w.
        direction :
            The direction of needle sample.
        half_width :
            Half of the sample width.

        Returns
        -------
        :
            True if coordinate should be included in sample locations, else False.
        """
        u, v, w = coords

        direction_conditions = {
            1: abs(u) < half_width and v <= 0 <= w,
            2: w <= 0 <= u and abs(v) < half_width,
            3: u <= 0 <= v and abs(w) < half_width,
            4: v <= 0 <= u and abs(w) < half_width,
            5: abs(u) < half_width and w <= 0 <= v,
            6: u <= 0 <= w and abs(v) < half_width,
        }
        return direction_conditions[direction] and (u + v + w) == 0
