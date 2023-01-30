from typing import List

import pandas as pd

from metrics.analysis.simulation import Simulation


class Sample:
    """
    Representation of a simulated sample.
    """

    @staticmethod
    def sample_data(coordinates: List[tuple], data: pd.DataFrame) -> pd.DataFrame:
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
