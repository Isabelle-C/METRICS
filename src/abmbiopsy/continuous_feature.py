class ContinuousFeature(Feature):
    """
    Representation of a continuous feature of simulated tumor or sample.
    """

    feature_type = "continuous"

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
