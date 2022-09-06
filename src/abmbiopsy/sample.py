from typing import List

import pandas as pd

from abmbiopsy.simulation import Simulation


class Sample:
    """
    Representation of a simulated sample.

    Sampling is intended to represent a clinical biopsy of a tumor. The
    punch samples represent punch biopsies, which use a circular blade to
    remove a tissue sample. The needle samples represent fine-needle
    aspiration biopsies, which use a hollow needle to remove a tissue
    sample.

    Attributes
    ----------
    shape : {'punch', 'needle'}
        Shape of the sample.
    radius : int
        Radius at which sample is taken.
    """

    def __init__(self, sample_shape: str, sample_radius: int):
        self.shape = sample_shape
        self.radius = sample_radius

    def __str__(self) -> str:
        attributes = [
            ("shape", self.shape),
            ("radius", self.radius),
        ]

        attribute_strings = [f"{key} = {value}" for key, value in attributes]
        string = " | ".join(attribute_strings)
        return f"SAMPLE [{string}]"

    def select_punch_sample_locations(self) -> list:
        """
        Get a list of punch sampling locations.

        Returns
        -------
        :
            Coordinates for punch sample locations.
        """

        punch_locations = [
            (u, v, w)
            for u in range(-self.radius + 1, self.radius)
            for v in range(-self.radius + 1, self.radius)
            for w in range(-self.radius + 1, self.radius)
            if (u + v + w) == 0 and (abs(u - 0) + abs(v - 0) + abs(w - 0)) / 2 <= self.radius
        ]
        return punch_locations

    def select_needle_sample_location(self, width: int) -> List[tuple]:
        """
        Get a list of needle sampling locations.

        Parameters
        ----------
        width : int
            Width of the sample.

        Returns
        -------
        :
            Coordinates for needle sample locations.
        """
        if (width % 2) == 0:
            raise ValueError("Width has to be an even number.")

        half_width = (width + 1) / 2

        return [
            (u, v, w)
            for u in range(-self.radius + 1, self.radius)
            for v in range(-self.radius + 1, self.radius)
            for w in range(-self.radius + 1, self.radius)
            if (u + v + w) == 0 and abs(u) < half_width and v <= 0 and w >= 0
        ]

    def sample_data(self, coordinates: List[tuple], data: pd.DataFrame) -> pd.DataFrame:
        """
        Extract sample from given data.

        Parameters
        ----------
        coordinates :
            Sample coordinates.
        data :
            Simulation data.

        Returns
        -------
        :
            Extracted sample data.
        """
        szudzik_coordinates = [Simulation.get_szudzik_pair(u, v) for u, v, _ in coordinates]

        sample_data = data[data["coordinate"].isin(szudzik_coordinates)]
        sample_data = sample_data.reset_index(drop=True)

        return sample_data
