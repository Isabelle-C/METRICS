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

    def compare_feature(self, sample_data: pd.DataFrame, simulation_data: pd.DataFrame) -> float:
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
        if self.name not in simulation_data.columns or self.name not in sample_data.columns:
            return float("nan")

        tumor_cdf = ECDF(simulation_data[self.name])
        sample_feature_data = list(sample_data[self.name])
        p_value = kstest(sample_feature_data, tumor_cdf)

        return p_value[1]
