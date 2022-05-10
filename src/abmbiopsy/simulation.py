import pandas as pd

from abmbiopsy.continuous_feature import ContinuousFeature
from abmbiopsy.discrete_feature import DiscreteFeature
from abmbiopsy.feature import Feature


class Simulation:
    """
    Container for simulated tumor object data.
    TODO: update docstring with attributes
    """

    def __init__(self, simulation_file: str):
        """
        Initialize Simulation.
        TODO: update docstring
        """
        self.file = simulation_file
        self.parse_file()
        self.parse_config()

    def __str__(self) -> str:
        attributes = [
            ("file", self.file),
            ("path", self.path),
            ("key", self.key),
            ("seed", self.seed),
            ("timepoints", self.timepoints),
            ("max_radius", self.max_radius),
        ]

        attribute_strings = [f"{key:10} = {value}" for key, value in attributes]
        string = "\n\t".join(attribute_strings)
        return "SIMULATION\n\t" + string

    def load_simulation(self, suffix=""):
        """
        TODO: add docstring
        """
        # TODO: load the simulation json as a dictionary
        #   - filename should be composed from attributes
        #   - include a possible suffix before the .json extension
        return {}

    def parse_file(self):
        """
        TODO: add docstring
        """
        # TODO
        # with the file name attribute, parse out values for:
        #   - the path to the file
        #   - the file key (file name without extension or seed)
        #   - the seed (as an integer)
        #   - the extension of the file
        self.path = ""
        self.key = ""
        self.seed = 0
        self.extension = ""

    def parse_config(self):
        """
        TODO: add docstring
        """
        # TODO: load the simulation (what method to call?) and parse out values for:
        #   - list of timepoints available in the simulation
        #   - the maximum radius of the simulation
        self.timepoints = []
        self.max_radius = 0

    def parse_timepoint(self, timepoint):
        """
        TODO: add docstring
        """
        # TODO: get the index of the timepoint

        # TODO: load in the simulation jsons for the main file and the .PARAM
        # file (what method to call? what specific parameter is helpful here?)

        # TODO: get the specified timepoint from the loaded json dictionaries

        # TODO: iterate through all the locations and cells in the timepoint to
        # parse out rows in the form of:
        #  [key, seed, timepoint, szudzik coordinate, u, v, w, z, position,
        #  population, state, volume, cycle, max_height, meta_pref, migra_threshold ]

        # TODO: get names of the feature columsn (what method to call?)

        # TODO: return parsed data as a dataframe
        return pd.DataFrame()

    @staticmethod
    def get_szudzik_pair(u, v):
        """
        TODO: add docstring
        """
        # TODO calculate szudzik pairing function for given signed values
        return 0

    @staticmethod
    def get_feature_list() -> list:
        """
        Return a list of valid Feature objects.

        Returns
        -------
        list
           List of Feature objects.
        """
        return [
            Feature("key", "TEXT", False),
            Feature("seed", "INTEGER", False),
            Feature("time", "REAL", False),
            Feature("coordinate", "INTEGER", False),
            Feature("u", "INTEGER", False),
            Feature("v", "INTEGER", False),
            Feature("w", "INTEGER", False),
            Feature("z", "INTEGER", False),
            Feature("p", "INTEGER", False),
            DiscreteFeature("population", "INTEGER", False, "A"),
            DiscreteFeature("state", "INTEGER", False, "A"),
            ContinuousFeature("volume", "REAL", False),
            ContinuousFeature("cycle", "REAL", True),
            ContinuousFeature("max_height", "REAL", False),
            ContinuousFeature("meta_pref", "REAL", False),
            ContinuousFeature("migra_threshold", "REAL", False),
        ]
