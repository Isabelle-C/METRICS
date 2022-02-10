class Sample:
    """
    Workflow for sampling biopsies from simulated tumor data.
    """

    def run_sample(input_path, sample_size, sample_shape, time, output_path):
        """
        Run workflow to extract samples from simulated tumor data.

        Sampling is intended to represent a clinical biopsy of a tumor. The
        punch samples represent punch biopsies, which use a circular blade to
        remove a tissue sample. The needle samples represent fine-needle
        aspiration biopsies, which use a hollow needle to remove a tissue
        sample.

        Parameters
        ----------
        input_path : str
            File path to simulated tumor data files.
        sample_size : int or list of int
            Radius or range of radii of sample taken.
        sample_shape : {'punch', 'needle'}
            Shape of the sample.
        time : float or list of floatine
            Time point(s) (in days) at which sample is taken.
        output_path : str
            File path for output sample data.
        """
        valid_sample_shape = {"needle", "punch"}
        if sample_shape not in valid_sample_shape:
            raise ValueError("results: sample_shape must be one of %r." % valid_sample_shape)

    def select_sample_location(input_path, sample_size, sample_shape, time):
        """
        Get a list of sampling locations for given sample conditions.

        Parameters
        ----------
        input_path : str
            File path to simulated tumor data files.
        sample_size : int or list of ints
            Radius or range of radii of sample taken.
        sample_shape : {'punch', 'needle'}
            Shape of the sample.
        time : float or list of float
            Time point(s) (in days) at which sample is taken.

        Returns
        -------
        loc_map : dict
            Dictionary with the locations in the whole tumor as sample
            simulation.
        """
        # TODO: edit the loc_map returns with keys and values in this dictionary. Likely tuples.
        pass

    def extract_simulation_sample(loc_map):
        """
        Extract simulated tumor data at specific sampling locations.

        Parameters
        ----------
        loc_map : dict
            Dictionary with the locations in the whole tumor as sample
            simulation.

        Returns
        -------
        sample_extract_df : DateFrame
            Samples produced from extracting tumor data at locations specified
            in loc_map.
        """
        pass

    def save_simulation_sample(output_path, sample_extract_df):
        """
        Save extracted samples to files.

        Parameters
        ----------
        output_path : str
            File path for output sample data.
        sample_extract_df : DateFrame
            Samples produced from extracting tumor data at locations specified
            in loc_map.
        """
        pass
