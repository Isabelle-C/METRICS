from typing import List
from os import path
import ntpath
import json

import pandas as pd
import numpy as np

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
        with open(file_name, "r", encoding="utf-8") as json_file:
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

    def parse_timepoint(self, timepoint: float) -> pd.DataFrame:
        """
        Parse data from simulation.

        Parameters
        ----------
        timepoint :
            Time point to parse simulation.

        Returns
        -------
        :
            Dataframe with simulation data.
        """

        loaded_simulation = self.load_simulation()
        loaded_param_simulation = self.load_simulation(suffix=".PARAM")

        if timepoint not in self.timepoints:
            raise ValueError("The timepoint not included in simulation file.")

        time_index = self.timepoints.index(timepoint)

        parsed_data = []
        sim_timepoint = loaded_simulation["timepoints"][time_index]["cells"]
        param_timepoint = loaded_param_simulation["timepoints"][time_index]["cells"]

        for (location, cells), (_, param_cells) in zip(sim_timepoint, param_timepoint):
            u = int(location[0])
            v = int(location[1])
            w = int(location[2])
            z = int(location[3])
            szudzik_coordinate = self.get_szudzik_pair(u, v)

            for cell, param_cell in zip(cells, param_cells):
                population = cell[1]
                state = cell[2]
                position = cell[3]
                volume = np.round(cell[4])
                cycle = np.round(np.mean(cell[5]))
                max_height = param_cell[5][3]
                meta_pref = param_cell[5][8]
                migra_threshold = param_cell[5][9]

                data_list = [
                    self.key,
                    self.seed,
                    timepoint,
                    szudzik_coordinate,
                    u,
                    v,
                    w,
                    z,
                    position,
                    population,
                    state,
                    volume,
                    cycle,
                    max_height,
                    meta_pref,
                    migra_threshold,
                ]

                parsed_data.append(data_list)

        columns = [feature.name for feature in self.get_feature_list()]
        return pd.DataFrame(parsed_data, columns=columns)

    @staticmethod
    def get_szudzik_pair(u: int, v: int) -> float:
        """
        Convert positions with positive or negative UV coordinates into a coordinate ID with
        signed Szudzik pairing function.
        A pairing function on a set associates each pair of numbers with a unique number through
        mathematical functions.
        Parameters
        ----------
        u :
            U coordinate of the position.
        v :
            V coordinate of the position.
        Returns
        -------
        float :
            The unique ID of the position coordinate.
        """
        if u >= 0:
            new_u = 2 * u
        else:
            new_u = (-2 * u) - 1

        if v >= 0:
            new_v = 2 * v
        else:
            new_v = (-2 * v) - 1

        if new_u >= new_v:
            return (new_u**2 + new_u + new_v) * 0.5
        else:
            return (new_v**2 + new_u) * 0.5

    @staticmethod
    def get_feature_list() -> List[Feature]:
        """
        Return a list of valid Feature objects.
        Returns
        -------
        List[Feature] :
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
