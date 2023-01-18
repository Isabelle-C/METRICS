from typing import List

from abmbiopsy.sample import Sample


class SamplePunch(Sample):
    """
    Representation of a simulated sample in punch shape.

    The punch samples represent punch biopsies, which use a circular
    blade to remove a tissue sample.

    Attributes
    ----------
    sample_radius :
        Radius at which sample is taken.
    """

    def __init__(self, sample_radius: int):
        self.sample_radius = sample_radius

    def get_sample_key(self) -> str:
        """
        Get key that describes sample method.

        Returns
        -------
        :
            Sample key which includes sampling method, sample radius, and center coordinate.
        """
        return f"punch-R{self.sample_radius}-(0,0,0)"

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
            for u in range(-self.sample_radius + 1, self.sample_radius)
            for v in range(-self.sample_radius + 1, self.sample_radius)
            for w in range(-self.sample_radius + 1, self.sample_radius)
            if (u + v + w) == 0 and (abs(u) + abs(v) + abs(w)) / 2 <= self.sample_radius
        ]
