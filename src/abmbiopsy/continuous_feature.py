from abmbiopsy.feature import Feature


class ContinuousFeature(Feature):
    """
    Representation of a continuous data feature.
    """

    feature_type = "continuous"

    def __str__(self):
        return "CONTINUOUS " + super().__str__()

    def compare_feature(self, sample_df, tumors_df):
        """
        Use statistical tests to compare continuous features.

        Uses Kolmogorov-Smirnov test to compare continuous feature between
        sample and tumor distributions. The Kolmogorov–Smirnov statistic
        quantifies a distance between the empirical distribution functions.

        Parameters
        ----------
        sample_df : DateFrame
            Loaded sample file
        tumors_df : DateFrame
            Loaded tumor file.

        Returns
        -------
        stats_result : float
            Result of statistical test.
        """

        # TODO: run KS test
        return 0
