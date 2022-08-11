import pandas as pd

from abmbiopsy.feature import Feature


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
    def get_feature_object(feature_name):
        """
        TODO: add docstring
        """
        # TODO: return an instnace of Feature for the given feature name
        #  - where do we get a list of Simulation features?
        #  - what subset of those features are valid feature to calculate
        #    statistics on?
        #  - what should happen if the given feature name doesn't exist OR is
        #    not valid?
        return Feature("", "", False)

    @staticmethod
    def get_feature_list() -> list:
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
