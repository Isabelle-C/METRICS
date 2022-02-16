class Simulation:
    """
    Container for simulated tumor object data.
    """

    def __init__(self):
        """
        Initialize Simulation.
        """
        pass

    def load_simulation_input(self, input_path):
        """
        Load one simulated tumor file into memory.

        Parameters
        ----------
        input_path : str
            File path to a simulation file.

        Returns
        -------
        loaded_simulation: dict
            Loaded simulation file.
        """
        pass

    def parse_simulation_input(self, output_path, loaded_simulation):
        """
        Convert raw simulation data into a Dataframe.

        Parameters
        ----------
        output_path : str
            File path for simulation data in matrix form.
        loaded_simulation : dict
            Loaded simulation file.

        Returns
        -------
        simulation_df : DateFrame
            Tumor simulation file in a Dataframe.
        """
        pass
        # TODO: save? Based on run time.
        # grab data from load simulation input

    def make_feature_list(self):
        """
        Return the list of valid features

        Returns
        -------
        feature_list : list
           List of valid features that can be extracted.
        """
        feature_list = [
            "APOPT",
            "QUIES",
            "MIGRA",
            "PROLI",
            "NECRO",
            "COUNT",
            "AVG CELL CYCLES",
            "CELL VOLUMES",
            "CROWDING TOLERANCE",
            "METABOLIC PREFERENCE",
            "MIGRATORY THRESHOLD",
        ]
        return feature_list
