from typing import List, Any, Tuple, Union

import numpy as np
import pandas as pd
from statsmodels.distributions.empirical_distribution import ECDF
from scipy.stats import entropy, kstest, gaussian_kde


from metrics.feature.feature import Feature


class ContinuousFeature(Feature):
    """
    Representation of a continuous data feature.

    Attributes
    ----------
    name :
        The name of the feature.
    affinity : {"NUMERIC", "INTEGER", "REAL", "TEXT", "BLOB"}
        The SQLite3 type affinity of the feature.
    is_null :
        True if feature data can be null, False otherwise.
    """

    feature_type = "continuous"
    """string: Type of the feature."""

    def __str__(self) -> str:
        return "CONTINUOUS " + super().__str__()

    def compare_feature_stat(
        self, sample_data: pd.DataFrame, simulation_data: pd.DataFrame
    ) -> float:
        """
        Uses statistical tests to compare continuous features.

        Uses Kolmogorov-Smirnov test to compare continuous feature between
        sample and tumor distributions. The Kolmogorov–Smirnov statistic
        quantifies a distance between the empirical distribution functions.

        Parameters
        ----------
        sample_data :
            Loaded sample data.
        simulation_data :
            Loaded tumor data.

        Returns
        -------
        :
            Result of statistical test.
        """
        if self.is_valid_feature_name(simulation_data, sample_data):
            sample = list(sample_data[self.name])
            reference = list(simulation_data[self.name])

            reference_cdf = ECDF(reference)
            p_value = kstest(sample, reference_cdf)
            return p_value[1]

        return float("nan")

    def compare_feature_info(
        self, sample_data: pd.DataFrame, simulation_data: pd.DataFrame
    ) -> float:
        """
        Uses Kullback-Leibler divergence (KL divergence) compare continuous features.

        Parameters
        ----------
        sample_data :
            Loaded sample data.
        simulation_data :
            Loaded tumor data.
        Returns
        -------
        :
            Result of KL divergence that are keyed by the category.
        """
        if self.is_valid_feature_name(simulation_data, sample_data):
            sample = list(sample_data[self.name])
            reference = list(simulation_data[self.name])

            sample_prob, reference_prob = self.get_pdfs(sample, reference)

            return entropy(sample_prob, reference_prob)

        return float("nan")

    def write_feature_data(
        self,
        data_list: list,
        stats: bool,
        info: bool,
        sample_data: pd.DataFrame,
        simulation_data: pd.DataFrame,
    ) -> List[Any]:
        """
        Writes feature data into the list of data.

        Parameters
        ----------
        data_list:
            List of data in analysis table.
        stats:
            True if calculating statistical tests, False otherwise.
        info:
            True if calculating KL divergence, False otherwise.
        sample_data :
            Loaded sample data.
        simulation_data :
            Loaded tumor data.

        Returns
        -------
        :
            List of data needed for analysis dataframe.
        """
        if stats and stats != info:
            stats_data = self.compare_feature_stat(sample_data, simulation_data)
            return [data_list + [None, stats_data]]

        if info and info != stats:
            info_data = self.compare_feature_info(sample_data, simulation_data)
            return [data_list + [None, info_data]]

        if info == stats == True:
            stats_data = self.compare_feature_stat(sample_data, simulation_data)
            info_data = self.compare_feature_info(sample_data, simulation_data)
            return [data_list + [None, stats_data, info_data]]

        return []

    def is_valid_feature_name(
        self, simulation_data: pd.DataFrame, sample_data: pd.DataFrame
    ) -> bool:
        """
        Parameters
        ----------
        simulation_data :
            Loaded tumor data.
        sample_data :
            Loaded sample data.

        Returns
        -------
        :
            True if feature name valid and if dataframe contains data, False otherwise.
        """

        if self.name not in simulation_data.columns or self.name not in sample_data.columns:
            return False
        if simulation_data[self.name].isna().all() or sample_data[self.name].isna().all():
            return False
        return True

    def get_pdfs(
        self, sample_data: list[float], reference_data: list[float]
    ) -> Union[Tuple[np.ndarray, np.ndarray], float]:
        """
        Parameters
        ----------
        reference_data :
            Distribution of the feature in the simulation data.
        sample_data :
            Distribution of the feature in the sample data.

        Returns
        -------
        :
            Probability density function of the feature.
        """
        try:
            # Estimate the probability density function (PDF) of the sample and simulation data
            reference_kde = gaussian_kde(reference_data)
            sample_kde = gaussian_kde(sample_data)
        except (ValueError, np.linalg.LinAlgError):
            # If the sample or simulation contain only a single unique value, the KDE will fail
            return float("nan")

        # Discretize continuous distributions into discrete approximations
        num_bins = 1000
        x = np.linspace(
            min(min(reference_data), max(sample_data)),
            max(min(reference_data), max(sample_data)),
            num_bins,
        )
        reference_prob = reference_kde.pdf(x)
        sample_prob = sample_kde.pdf(x)

        return sample_prob, reference_prob
