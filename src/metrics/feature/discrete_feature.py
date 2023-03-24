from typing import Dict, List, Any, Union


import pandas as pd
from scipy.stats import hypergeom, entropy

from metrics.feature.feature import Feature


class DiscreteFeature(Feature):
    """
    Representation of a discrete data feature.

    Attributes
    ----------
    name :
        The name of the feature.
    affinity : {"NUMERIC", "INTEGER", "REAL", "TEXT", "BLOB"}
        The SQLite3 type affinity of the feature.
    is_null :
        True if feature data can be null, False otherwise.
    """

    feature_type = "discrete"
    """string: Type of the feature."""

    def __init__(self, name: str, affinity: str, is_null: bool):
        super().__init__(name, affinity, is_null)

    def __str__(self) -> str:
        return "DISCRETE " + super().__str__()

    def compare_feature_stat(
        self, sample_data: pd.DataFrame, simulation_data: pd.DataFrame
    ) -> Union[Dict[str, Any], float]:
        """
        Uses statistical tests to compare discrete features.

        Uses hypergeometric test to compare discrete feature between sample
        and true distributions. Hypergeometric distribution describes the
        probability of k successes in N draws, without replacement, from a
        finite population of size M that contains exactly n objects.

        Parameters
        ----------
        sample_data :
            Loaded sample data.
        simulation_data :
            Loaded tumor data.

        Returns
        -------
        :
            Result of statistical tests that are keyed by the category.
        """
        hypergeom_pmfs = {}
        if self.name not in simulation_data.columns or self.name not in sample_data.columns:
            return float("nan")

        sample = list(sample_data[self.name])
        reference = list(simulation_data[self.name])

        N = len(sample)
        M = len(reference)

        categories = sorted(set(reference))
        for category in categories:
            k = self.get_count(sample, category)
            n = self.get_count(reference, category)
            hypergeom_pmfs[category] = hypergeom.pmf(k, M, n, N)

        return hypergeom_pmfs

    def compare_feature_info(
        self, sample_data: pd.DataFrame, simulation_data: pd.DataFrame
    ) -> float:
        """
        Uses KL-divergence to compare discrete features.

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
        if self.name not in simulation_data.columns or self.name not in sample_data.columns:
            return float("nan")

        sample = list(sample_data[self.name])
        reference = list(simulation_data[self.name])

        sample_dist = []
        simulation_dist = []

        categories = sorted(set(reference))
        for category in categories:
            sample_dist.append(self.get_count(sample, category))
            simulation_dist.append(self.get_count(reference, category))

        sample_pdf = [x / len(sample) for x in sample_dist]
        simulation_pdf = [x / len(reference) for x in simulation_dist]
        return entropy(sample_pdf, simulation_pdf)

    def write_feature_data(
        self,
        data_list: list,
        sample_data: pd.DataFrame,
        simulation_data: pd.DataFrame,
    ) -> List[Any]:
        """
        Uses KL-divergence compare continuous features.

        Parameters
        ----------
        data_list:
            List of data in analysis table.
        sample_data :
            Loaded sample data.
        simulation_data :
            Loaded tumor data.

        Returns
        -------
        :
            List of data needed for analysis dataframe.
        """
        output_list = []

        stats_data = self.compare_feature_stat(sample_data, simulation_data)
        info_data = self.compare_feature_info(sample_data, simulation_data)

        if not isinstance(stats_data, float):
            for key, value in stats_data.items():
                output_list.append(data_list + [key] + [value, info_data])
            return output_list

        return []

    @staticmethod
    def get_count(data: list, category: str) -> int:
        """
        Returns the number of categories of the feature.

        Parameters
        ----------
        data :
            Loaded data.
        category :
            Categories of data.

        Returns
        -------
        :
            Number of categories of the feature.
        """
        return data.count(category)
