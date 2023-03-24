from typing import List, Union
import pandas as pd

from metrics.analysis.experiment import Experiment
from metrics.analysis.simulation import Simulation
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
    experiment : Experiment
        Experiment object.
    timepoint : float
        Time point to execute statistical test.
    observation_timepoint : float
        Time point of observation to execute statistical test.
    features : List[Union[ContinuousFeature, DiscreteFeature][
        Feature object.
    """

    def __init__(
        self,
        simulation_key: str,
        experiment: Experiment,
        timepoint: float,
        observation_timepoint: float,
        features: List[Union[ContinuousFeature, DiscreteFeature]],
    ):
        self.key = simulation_key
        self.experiment = experiment
        self.timepoint = timepoint
        self.observation_timepoint = observation_timepoint
        self.features = features

    def __str__(self) -> str:
        attributes = [
            ("key", self.key),
            ("experiment", self.experiment.comparison_group),
            ("reference_timepoint", self.timepoint),
            ("observation_timepoint", self.observation_timepoint),
            ("features", [feature.name for feature in self.features]),
        ]

        attribute_strings = [f"{key:10} = {value}" for key, value in attributes]
        string = "\n\t".join(attribute_strings)
        return "ANALYSIS\n\t" + string

    @staticmethod
    def extract_sample_data(
        sample: Union[SampleNeedle, SamplePunch], simulation_data: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Extract sample from simulation data.

        Parameters
        ----------
        sample : Union[SampleNeedle,SamplePunch]
            Sample object.
        simulation_data : pd.DataFrame
            Simulation data.

        Returns
        -------
        sample_data : pd.DataFrame
            Extracted sample data.
        """
        sample_locations = sample.select_sample_locations()
        sample_data = sample.sample_data(sample_locations, simulation_data)
        return sample_data

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
            [self.calculate_feature(data, feature) for feature in self.features],
            axis=0,
        )
        return stats_df.fillna(value="NULL")

    def calculate_feature(
        self, data: pd.DataFrame, feature: Union[ContinuousFeature, DiscreteFeature]
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
        """
        object_dict: dict = self.experiment.create_experiment_dict()

        reference: Union[SampleNeedle, SamplePunch, Simulation] = object_dict["reference"]
        observation: Union[SampleNeedle, SamplePunch, Simulation] = object_dict["observation"]

        simulation_data = data[(data["time"] == self.timepoint) & (data["key"] == self.key)]
        if isinstance(reference, (SampleNeedle, SamplePunch)):
            reference_data = self.extract_sample_data(reference, simulation_data)
            reference_key = reference.get_sample_key()
        elif isinstance(reference, Simulation):
            reference_data = simulation_data
            reference_key = "simulation"

        observation_simulation_data = data[
            (data["time"] == self.observation_timepoint) & (data["key"] == self.key)
        ]
        if isinstance(observation, (SampleNeedle, SamplePunch)):
            observation_data = self.extract_sample_data(observation, observation_simulation_data)
            observation_key = observation.get_sample_key()
        elif isinstance(observation, Simulation):
            observation_data = observation_simulation_data
            observation_key = "simulation"

        analysis_data = []

        for seed, reference_seed_data in reference_data.groupby("seed"):
            observation_seed_data = observation_data[observation_data["seed"] == seed]

            data_list = [
                self.experiment.comparison_group,
                self.key,
                seed,
                self.timepoint,
                self.observation_timepoint,
                reference_key,
                observation_key,
                feature.name,
            ]

            output_data = feature.write_feature_data(
                data_list, observation_seed_data, reference_seed_data
            )
            analysis_data.extend(output_data)

        columns = [analysis_feature.name for analysis_feature in self.get_feature_list()]
        return pd.DataFrame(analysis_data, columns=columns)

    @staticmethod
    def get_feature_list() -> List[Feature]:
        """
        Return a list of valid Feature objects.

        Returns
        -------
        :
           List of Feature objects.
        """
        feature_columns = [
            Feature("comparison_group", "TEXT", False),
            Feature("key", "TEXT", False),
            Feature("seed", "INTEGER", False),
            Feature("reference_time", "REAL", False),
            Feature("obervation_time", "REAL", False),
            Feature("reference_key", "TEXT", False),
            Feature("obervation_key", "TEXT", False),
            Feature("feature", "TEXT", False),
            Feature("category", "TEXT", False),
            Feature("pvalue", "REAL", False),
            Feature("divergence", "REAL", False),
        ]

        return feature_columns
