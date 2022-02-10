class DiscreteFeature(Feature):
    """
    Representation of a discrete feature of simulated tumor or sample.
    """

    feature_type = "discrete"

    def compare_feature(self, sample_df, tumors_df):
        """
        Use statistical tests to compare discrete features.

        Uses hypergeometric test to compare discrete feature between sample
        and true distributions. Hypergeometric distribution describes the
        probability of k successes in n draws, without replacement, from a
        finite population of size N that contains exactly K objects.

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

        pass
        # TODO: run hypergeometric test
