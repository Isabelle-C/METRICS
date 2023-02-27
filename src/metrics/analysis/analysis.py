from typing import List, Union
import pandas as pd

from metrics.feature.continuous_feature import ContinuousFeature
from metrics.feature.discrete_feature import DiscreteFeature
from metrics.feature.feature import Feature
from metrics.sample.sample_needle import SampleNeedle
from metrics.sample.sample_punch import SamplePunch


class Analysis:
    """
    Workflow for statistical testing on features of simulated tumor sample data.

    Attributes
    ----------
    key : str
        Simulation key.
    sample : Sample
        Sample object.
    timepoint : float
        Time point to execute statistical test.
    features : List[Union[ContinuousFeature, DiscreteFeature][
        Feature object.
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
            ("sample", self.sample),
            ("timepoint", self.timepoint),
            ("features", self.features),
        ]

        attribute_strings = [f"{key:10} = {value}" for key, value in attributes]
        string = "\n\t".join(attribute_strings)
        return "ANALYSIS\n\t" + string

    def calculate_features(self, data: pd.DataFrame, stats: bool, info: bool) -> pd.DataFrame:
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
            [self.calculate_feature(data, feature, stats, info) for feature in self.features],
            axis=0,
        )

        return stats_df.fillna(value="NULL")

    def calculate_feature(
        self,
        data: pd.DataFrame,
        feature: Union[ContinuousFeature, DiscreteFeature],
        stats: bool,
        info: bool,
    ) -> pd.DataFrame:
        """
        Calculate statistical comparison of a feature between a sample and the simulation
        population.

        Parameters
        ----------
        data :
            Simulation data.
        feature :
            Feature object.
        stats :
            True if calculating statistical tests, False otherwise.
        info :
            True if calculating KL divergence, False otherwise.
        """
        simulation_data = data[(data["time"] == self.timepoint) & (data["key"] == self.key)]

        sample_locations = self.sample.select_sample_locations()
        sample_data = self.sample.sample_data(sample_locations, simulation_data)

        analysis_data = []

        for seed, simulation_seed_data in simulation_data.groupby("seed"):
            sample_seed_data = sample_data[sample_data["seed"] == seed]

            data_list = [
                self.key,
                seed,
                self.timepoint,
                self.timepoint,
                self.sample.get_sample_key(),
                feature.name,
            ]

            output_data = feature.write_feature_data(
                data_list, stats, info, sample_seed_data, simulation_seed_data
            )
            analysis_data.extend(output_data)

        columns = [analysis_feature.name for analysis_feature in self.get_feature_list(stats, info)]
        return pd.DataFrame(analysis_data, columns=columns)

    @staticmethod
    def get_feature_list(stats: bool, info: bool) -> List[Feature]:
        """
        Return a list of valid Feature objects.

        Parameters
        ----------
        stats :
            True if calculating statistical tests, False otherwise.
        info :
            True if calculating KL divergence, False otherwise.

        Returns
        -------
        :
           List of Feature objects.
        """
        base_columns = [
            Feature("key", "TEXT", False),
            Feature("seed", "INTEGER", False),
            Feature("tumor_time", "REAL", False),
            Feature("sample_time", "REAL", False),
            Feature("sample_key", "TEXT", False),
            Feature("feature", "TEXT", False),
            Feature("category", "TEXT", False),
        ]
        feature_columns = base_columns

        if stats and not info:
            feature_columns += [Feature("pvalue", "REAL", False)]
        if info and not stats:
            feature_columns += [Feature("divergence", "REAL", False)]
        if stats and info:
            feature_columns += [
                Feature("pvalue", "REAL", False),
                Feature("divergence", "REAL", False),
            ]

        return feature_columns
