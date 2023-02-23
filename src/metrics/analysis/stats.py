from typing import List, Union
import pandas as pd

from metrics.feature.continuous_feature import ContinuousFeature
from metrics.feature.discrete_feature import DiscreteFeature
from metrics.feature.feature import Feature
from metrics.sample.sample_needle import SampleNeedle
from metrics.sample.sample_punch import SamplePunch


class Stats:
    """
    Workflow for statistical testing on features of simulated tumor sample data.

    Attributes
    ----------
    key :
        Simulation key.
    sample :
        Sample object.
    timepoint :
        Time point to execute statistical test.
    features :
        Feature objects.
    """

    def __init__(
        self,
        simulation_key: str,
        sample: Union[SampleNeedle, SamplePunch],
        timepoint: float,
        features: List[Union[ContinuousFeature, DiscreteFeature]],
    ):
        self.key = simulation_key
        self.sample = sample
        self.timepoint = timepoint
        self.features = features

    def __str__(self) -> str:
        attributes = [
            ("key", self.key),
            ("sample", self.sample.get_sample_key()),
            ("timepoint", self.timepoint),
            ("feature", [feature.name for feature in self.features]),
        ]

        attribute_strings = [f"{key:10} = {value}" for key, value in attributes]
        string = "\n\t".join(attribute_strings)
        return "STATS\n\t" + string

    def calculate_feature(
        self, data: pd.DataFrame, feature: Union[ContinuousFeature, DiscreteFeature]
    ) -> pd.DataFrame:
        """
        Calculate statistical comparison of a feature between a sample and the simulation population.

        Parameters
        ----------
        data :
            Simulation data.
        feature :
            Feature object.

        Returns
        -------
        :
            Stats data calculated with the given feature.
        """
        simulation_data = data[(data["time"] == self.timepoint) & (data["key"] == self.key)]

        sample_locations = self.sample.select_sample_locations()
        sample_data = self.sample.sample_data(sample_locations, simulation_data)

        stats_data = []

        for seed, simulation_seed_data in simulation_data.groupby("seed"):
            sample_seed_data = sample_data[sample_data["seed"] == seed]

            feature_data = feature.compare_feature(sample_seed_data, simulation_seed_data)

            data_list = [
                self.key,
                seed,
                self.timepoint,
                self.timepoint,
                self.sample.get_sample_key(),
                feature.name,
            ]

            if isinstance(feature_data, dict):
                for dict_key, dict_stat in feature_data.items():
                    stats_data.append(data_list + [dict_key, dict_stat])
            else:
                data_list = data_list + [None, feature_data]
                stats_data.append(data_list)

        columns = [stats_feature.name for stats_feature in self.get_feature_list()]
        return pd.DataFrame(stats_data, columns=columns)

    def calculate_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate statistical comparison of features between a sample and the simulation population.

        Parameters
        ----------
        data :
            Simulation data.

        Returns
        -------
        :
            Stats data calculated with the given features.
        """
        stats_df = pd.concat(
            [self.calculate_feature(data, feature) for feature in self.features], axis=0
        )

        return stats_df.fillna(value="NULL")

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
            Feature("sample_key", "TEXT", False),
            Feature("feature", "TEXT", False),
            Feature("category", "TEXT", False),
            Feature("pvalue", "REAL", False),
        ]
