from typing import List

import pandas as pd

from abmbiopsy.continuous_feature import ContinuousFeature
from abmbiopsy.discrete_feature import DiscreteFeature
from abmbiopsy.feature import Feature
from abmbiopsy.simulation import Simulation


class Stats:
    """
    Workflow for statistical testing on features of simulated tumor sample data.
    TODO: update docstring
    """

    def __init__(self, simulation_key, sample, timepoint):
        """
        Initialize Simulation.
        TODO: update docstring
        """
        self.key = simulation_key
        self.sample = sample
        self.timepoint = timepoint

    def __str__(self) -> str:
        attributes = [
            ("key", self.key),
            ("sample", self.sample),
            ("timepoint", self.timepoint),
        ]

        attribute_strings = [f"{key:10} = {value}" for key, value in attributes]
        string = "\n\t".join(attribute_strings)
        return "STATS\n\t" + string

    def calculate_feature(self, feature, data):
        """
        TODO: add docstring
        """
        # TODO: get instance of feature object given feature name (what method
        # to call?)

        # TODO: iterate through each seed, filter the data for the relevant
        # timepoint, sample the data (what method? where to get the sample?),
        # and create rows in the form of:
        #  [key, seed, timepoint for the tumor, timepoint for the sample,
        #  sample_type, sample radius, feature name, p value]

        # TODO: get names of the feature columsn (what method to call?)

        # TODO: return parsed data as a dataframe
        return pd.DataFrame()

    @staticmethod
    def get_feature_object(feature_name: str) -> Feature:
        """
        Return feature object valid for statistics calculation.

        Parameters
        ----------
        feature_name :
            Name of feature.

        Returns
        -------
        :
            Feature object.
        """
        feature_list = Simulation.get_feature_list()

        for feature in feature_list:
            if feature.name == feature_name:
                if isinstance(feature, ContinuousFeature) or isinstance(feature, DiscreteFeature):
                    return feature
                else:
                    raise ValueError("Feature is not valid for statistics calculation.")
        raise ValueError("Feature does not exist.")

    @staticmethod
    def get_feature_list() -> List[Feature]:
        """
        Return a list of valid Feature objects.

        Returns
        -------
        :
           List of Feature objects.
        """
        return [
            Feature("key", "TEXT", False),
            Feature("seed", "INTEGER", False),
            Feature("tumor_time", "REAL", False),
            Feature("sample_time", "REAL", False),
            Feature("sample_type", "TEXT", False),
            Feature("sample_radius", "INTEGER", False),
            Feature("feature", "TEXT", False),
            Feature("pvalue", "REAL", False),
        ]
