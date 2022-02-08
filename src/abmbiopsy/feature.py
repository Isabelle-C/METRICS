class Feature:
    """
    Representation of a simulated tumor or sample feature.
    """

    def __init__(self, name):
        """
        Initialize Feature with name.

        Parameters
        ----------
        name : str
            The name of the feature.
        """
        self.name = name

    def compare_feature(self, sample_df, tumors_df):
        """
        Calculate statistical similarity between two feature distributions.

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
