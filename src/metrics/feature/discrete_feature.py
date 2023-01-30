from typing import Dict, List
import pandas as pd
from scipy.stats import hypergeom

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

    def __init__(self, name: str, affinity: str, is_null: bool, categories: List[str]):
        super().__init__(name, affinity, is_null)
        self.categories = categories

    def __str__(self) -> str:
        return "DISCRETE " + super().__str__()

    def compare_feature(
        self, sample_dataframe: pd.DataFrame, tumors_dataframe: pd.DataFrame
    ) -> Dict[str, float]:
        """
        Uses statistical tests to compare discrete features.

        Uses hypergeometric test to compare discrete feature between sample
        and true distributions. Hypergeometric distribution describes the
        probability of k successes in N draws, without replacement, from a
        finite population of size M that contains exactly n objects.

        Parameters
        ----------
        sample_dataframe :
            Loaded sample data.
        tumors_dataframe :
            Loaded tumor data.

        Returns
        -------
        :
            Result of statistical tests that are keyed by the category.
        """
        hypergeom_pmfs = {}
        if self.name not in tumors_dataframe.columns or self.name not in sample_dataframe.columns:
            hypergeom_pmfs = {category: float("nan") for category in self.categories}
            return hypergeom_pmfs

        M = len(tumors_dataframe)
        N = len(sample_dataframe)
        for category in self.categories:
            k = list(sample_dataframe[self.name]).count(category)
            n = list(tumors_dataframe[self.name]).count(category)
            hypergeom_pmfs[category] = hypergeom.pmf(k, M, n, N)

        return hypergeom_pmfs
