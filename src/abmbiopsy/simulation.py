from typing import List
from os import path
import ntpath
import json

import pandas as pd

from abmbiopsy.continuous_feature import ContinuousFeature
from abmbiopsy.discrete_feature import DiscreteFeature
from abmbiopsy.feature import Feature


class Simulation:
    """
    Container for simulated tumor object data.

    Attributes
    ----------
    file : str
        Path and file name for the simulation file.
    path : str
        Directory to the folder of simulation file.
    key : str
        File name without extension or seed.
    seed : int
        Seed of the simulation.
    extension : str
        Extension of the simulation file.
    timepoints : List[float]
        Time point(s) (in days) in the simulation file.
    max_radius : int
        Maximum radius of the simulation.
    """

    def __init__(self, simulation_file: str):
        self.file = simulation_file
        self.path: str = ""
        self.key: str = ""
        self.seed: int = 0
        self.extension: str = ""
        self.timepoints: List[float] = []
        self.max_radius: int = 0

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

    def load_simulation(self, suffix: str = "") -> dict:
        """
        Load simulation file into memory.

        Parameters
        ----------
        suffix :
            Suffix of the file.

        Returns
        -------
        dict :
            Loaded simulation file.
        """
        file_name = f"{self.path}/{self.key}_{self.seed:02}{suffix}{self.extension}"
        with open(file_name, "r") as json_file:
            loaded_simulation = json.load(json_file)
        return loaded_simulation

    def parse_file(self) -> None:
        """
        Parse out attributes from file name.
        """
        self.path = ntpath.dirname(self.file)
        base = ntpath.basename(self.file)
        remove_extension = path.splitext(base)[0]
        remove_suffix = path.splitext(remove_extension)[0]
        self.extension = path.splitext(base)[1]
        self.key = remove_suffix[:-3]

    def parse_config(self) -> None:
        """
        Parse out attributes from loaded simulation file.
        """
        loaded_simulation = self.load_simulation()
        self.timepoints = [tp["time"] for tp in loaded_simulation["timepoints"]]
        self.max_radius = loaded_simulation["config"]["size"]["radius"]
        self.seed = loaded_simulation["seed"]

    def parse_timepoint(self, timepoint: list) -> pd.DataFrame:
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
    def get_szudzik_pair(u: float, v: float) -> float:
        """
        TODO: add docstring
        """
        # TODO calculate szudzik pairing function for given signed values
        return 0.0

    @staticmethod
    def get_feature_list() -> list:
        """
        Return a list of valid Feature objects.

        Returns
        -------
        list :
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
