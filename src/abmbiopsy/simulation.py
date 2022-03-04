import pandas as pd

from abmbiopsy.feature import Feature
from abmbiopsy.continuous_feature import ContinuousFeature
from abmbiopsy.discrete_feature import DiscreteFeature


class Simulation:
    """
    Container for simulated tumor object data.
    TODO: update docstring with attributes
    """

    def __init__(self, simulation_file):
        """
        Initialize Simulation.
        TODO: update docstring
        """
        self.file = simulation_file
        self.parse_file()
        self.parse_config()

    def __str__(self):
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
    def get_feature_list():
        """
        Return the list of valid features

        Returns
        -------
        feature_list : list
           List of valid features that can be extracted.

        TODO: update docstring
        """
        return [
            Feature("key", "string", False),
            Feature("seed", "int", False),
            Feature("time", "float", False),
            Feature("coordinate", "int", False),
            Feature("u", "int", False),
            Feature("v", "int", False),
            Feature("w", "int", False),
            Feature("z", "int", False),
            Feature("p", "int", False),
            DiscreteFeature("population", "int", False),
            DiscreteFeature("state", "int", False),
            ContinuousFeature("volume", "float", False),
            ContinuousFeature("cycle", "float", True),
            ContinuousFeature("max_height", "float", False),
            ContinuousFeature("meta_pref", "float", False),
            ContinuousFeature("migra_threshold", "float", False),
        ]
