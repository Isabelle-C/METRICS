class Stats:
    """
    Workflow for statistical testing on features of simulated tumor sample data.
    """

    def run_stats(self,input_sample_path, input_tumor_path, output_path, feature):
        """
        Run workflow to perform statistical tests to compare simulation and
        sample data.

        Parameters
        ----------
        input_sample_path : str
            File path to sample files.
        input_tumor_path : str
            File path to tumor files.
        output_path : str
            File path for statistical analysis files.
        feature : str or list of str
            Features for statistical test.
        """

        pass

    def load_sample_file(self,input_path):
        """
        Load parsed sample simulation into memory.

        Parameters
        ----------
        input_path : str
            File path to sample files.

        Returns
        -------
        sample_df : DateFrame
           Loaded sample file.
        """
        pass

    def load_tumor_file(self,input_path):
        """
        Load parsed tumor simulation into memory.

        Parameters
        ----------
        input_path : str
            File path to tumor files.

        Returns
        -------
        tumors_df : DateFrame
            Loaded tumor file.
        """
        pass

    def get_feature(self,feature_list):
        """
        Parse feature list input into lists of Feature objects.

        Parameters
        ----------
        feature_list : list of str
            Features for statistical test.

        Returns
        -------
        feature_objects : list
            List of Feature objects.
        """
        # TODO: Edit the feature_list param in docstring
        # TODO: determine what the code would look like and add extended description in docstring
        pass

    def compare_features(self,sample_df, tumors_df, feature_objects):
        """
        Run statistical tests on each feature.

        Parameters
        ----------
        sample_df : DateFrame
            Loaded sample file
        tumors_df : DateFrame
            Loaded tumor file.
        feature_objects : list
            List of Feature objects.

        Returns
        -------
        stats_dict : dict
            Result of statistical tests.
        """

        # TODO: extract the feature list from input lists

        pass

    def save_features(self,output_path, stats_df):
        """
        Save statistical test results to files.

        Parameters
        ----------
        output_path : str
            File path for statistical analysis files.
        stats_df : DateFrame
            Result of statistical tests.
        """
        pass
