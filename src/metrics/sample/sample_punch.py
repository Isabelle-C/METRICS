from typing import List
import warnings

from metrics.analysis.coordinate import Coordinate
from metrics.sample.sample import Sample


class SamplePunch(Sample):
    """
    Representation of a simulated sample in punch shape.

    The punch samples represent punch biopsies, which use a circular
    blade to remove a tissue sample.

    Attributes
    ----------
    simulation_radius : int
        Radius of the simulation.
    sample_radius : int
        Radius at which sample is taken.
    center : Coordinate
        Center of the punch sample.
    """

    def __init__(self, simulation_radius: int, sample_radius: int, center: tuple):
        distance_from_center = [abs(i - sample_radius) for i in center] + [
            abs(i + sample_radius) for i in center
        ]
        if max(distance_from_center) > simulation_radius:
            raise ValueError("The punch center exceed the simulation edge")
        if max(distance_from_center) == simulation_radius:
            warnings.warn("The punch right on the edge of simulation.")

        self.simulation_radius = simulation_radius
        self.sample_radius = sample_radius
        self.center = Coordinate(center)

    def get_sample_key(self) -> str:
        """
        Get key that describes sample method.

        Returns
        -------
        :
            Sample key which includes sampling method, sample radius, and center coordinate.
        """
        return f"punch-R{self.sample_radius}-{self.center.key}"

    def select_sample_locations(self) -> List[tuple]:
        """
        Get a list of punch sampling locations.

        Returns
        -------
        :
            Coordinates for punch sample locations.
        """
        return [
            (u, v, w)
            for u in range(self.center.u - self.sample_radius, self.center.u + self.sample_radius)
            for v in range(self.center.v - self.sample_radius, self.center.v + self.sample_radius)
            for w in range(self.center.w - self.sample_radius, self.center.w + self.sample_radius)
            if (u + v + w) == 0
            and (abs(u - self.center.u) + abs(v - self.center.v) + abs(w - self.center.w)) / 2
            <= (self.sample_radius - 1)
        ]
