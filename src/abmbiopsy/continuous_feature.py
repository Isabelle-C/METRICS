import pandas as pd
from statsmodels.distributions.empirical_distribution import ECDF
from scipy.stats import kstest

from abmbiopsy.feature import Feature


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

    def compare_feature(
        self, sample_dataframe: pd.DataFrame, tumors_dataframe: pd.DataFrame
    ) -> float:
        """
        Uses statistical tests to compare continuous features.

        Uses Kolmogorov-Smirnov test to compare continuous feature between
        sample and tumor distributions. The Kolmogorov–Smirnov statistic
        quantifies a distance between the empirical distribution functions.

        Parameters
        ----------
        sample_dataframe :
            Loaded sample data.
        tumors_dataframe :
            Loaded tumor data.

        Returns
        -------
        float
            Result of statistical test.
        """
        if self.name not in tumors_dataframe.columns or self.name not in sample_dataframe.columns:
            return float("nan")

        tumor_cdf = ECDF(tumors_dataframe[self.name])
        sample_feature_data = list(sample_dataframe[self.name])
        p_value = kstest(sample_feature_data, tumor_cdf)

        return p_value[1]
