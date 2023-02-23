from typing import Dict, List, Any
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
    categories :
        Categories of the feature.
    """

    feature_type = "discrete"
    """string: Type of the feature."""

    def __init__(self, name: str, affinity: str, is_null: bool, categories: List[int]):
        super().__init__(name, affinity, is_null)
        self.categories = categories

    def __str__(self) -> str:
        return "DISCRETE " + super().__str__()

    def compare_feature_stat(
        self, sample_data: pd.DataFrame, simulation_data: pd.DataFrame
    ) -> Dict[str, float]:
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
            hypergeom_pmfs = {category: float("nan") for category in self.categories}
            return hypergeom_pmfs

        M = len(simulation_data)
        N = len(sample_data)

        categories = sorted(set(simulation_data[self.name]))
        for category in categories:
            k = list(sample_data[self.name]).count(category)
            n = list(simulation_data[self.name]).count(category)
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
        kl_divergence = {}
        if self.name not in simulation_data.columns or self.name not in sample_data.columns:
            kl_divergence = float("nan")
            return kl_divergence

        sample_dist = []
        simulation_dist = []
        categories = sorted(set(simulation_data[self.name]))
        for category in categories:
            sample_dist.append(list(sample_data[self.name]).count(category) / len(sample_data))
            simulation_dist.append(
                list(simulation_data[self.name]).count(category) / len(simulation_data)
            )

        kl_divergence = entropy(sample_dist, simulation_dist)
        return kl_divergence

    def write_feature_data(
        self,
        data_list: list,
        stats: bool,
        info: bool,
        sample_data: pd.DataFrame,
        simulation_data: pd.DataFrame,
    ) -> List[Any]:
        """
        Uses KL-divergence compare continuous features.

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
        output_list = []

        if stats != info:
            if stats:
                data = self.compare_feature_stat(sample_data, simulation_data)
            if info:
                data = self.compare_feature_info(sample_data, simulation_data)

            for dict_key, dict_data in data.items():
                output_list.append(data_list + [dict_key, dict_data])
            return output_list

        elif info == stats == True:
            stats_data = self.compare_feature_stat(sample_data, simulation_data)
            info_data = self.compare_feature_info(sample_data, simulation_data)

            for key, value in stats_data.items():
                output_list.append(data_list + [key] + [value, info_data[key]])
            return output_list

        return []
