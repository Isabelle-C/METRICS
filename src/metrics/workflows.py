from typing import List

from metrics.analysis.analysis import Analysis
from metrics.analysis.database import Database
from metrics.analysis.experiment import Experiment
from metrics.analysis.simulation import Simulation

SIMULATION_TABLE = "simulations"
ANALYSIS_TABLE = "stats"


def run_parse_simulations(
    database_file: str, simulation_path: str, seed: str, timepoints: List[float]
) -> None:
    """
    Parse the simulation and write data into databse file.

    Parameters
    ----------
    database_file :
        File path to the database file.
    simulation_path :
        File path to a folder of simulation files.
    seed :
        The seed of simulation file.
    timepoints :
        The timepoints to parse the simulation data.
    """
    simulation_file = f"{simulation_path}_{seed}.json"

    database = Database(database_file)
    simulation = Simulation(simulation_file)
    # database.drop_table(SIMULATION_TABLE)
    database.create_table(SIMULATION_TABLE, simulation)

    # print(simulation)

    for timepoint in timepoints:
        simulation_df = simulation.parse_timepoint(timepoint)
        database.add_dataframe(SIMULATION_TABLE, simulation_df)


def run_calculate_analysis(
    database_path: str,
    simulation_path: str,
    seed: str,
    features: list[str],
    timepoints: list[float],
    observation_timepoints: list[float],
    samples: dict,
    comparisons: dict,
) -> None:
    """
    Run the statistical test on data with the specified feature and sampling method.

    Parameters
    ----------
    database_path :
        File path to the database file for reading simulation and for writing stats.
    simulation_path :
        File path to a folder of simulation files.
    seed :
        The seed of simulation file.
    features :
        The name of the features.
    timepoints :
        The timepoints to perform statistical test.
    observation_timepoints :
        The timepoints of observations to perform statistical test.
    samples :
        Sample parameter definitions.
    comparisons :
        The comparisons to perform.
    """
    simulation_file = f"{simulation_path}_{seed}.json"

    database = Database(database_path)
    simulation = Simulation(simulation_file)

    data = database.load_dataframe(SIMULATION_TABLE, simulation.key)
    data = data[data["seed"] == int(seed)]

    # database.drop_table(ANALYSIS_TABLE)

    for comparison in comparisons.values():
        # for key, value in comparison.items():
        #    print(f"{key} = {value}")
        # print(f"seed = {seed}")
        # print(f"reference timepoint | observation timepoint")
        # print("--------------------------------------------")
        for timepoint in timepoints:
            for observation_timepoint in observation_timepoints:
                if timepoint == observation_timepoint:
                    experiment = Experiment(comparison, samples, simulation)

                    analysis = Analysis(
                        simulation.key,
                        experiment,
                        timepoint,
                        observation_timepoint,
                        [Simulation.get_feature_object(feature) for feature in features],
                    )
                    analysis_df = analysis.calculate_features(data)

                    database.create_table(ANALYSIS_TABLE, analysis)
                    database.add_dataframe(ANALYSIS_TABLE, analysis_df)

                    # print(f"{timepoint}{' ' *(20-len(str(timepoint)))}| {observation_timepoint}")

        # print("\n")
