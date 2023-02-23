from typing import Union, List

from metrics.analysis.database import Database
from metrics.analysis.simulation import Simulation
from metrics.sample.sample_needle import SampleNeedle
from metrics.sample.sample_punch import SamplePunch
from metrics.analysis.analysis import Analysis

SIMULATION_TABLE = "simulation"
ANALYSIS_TABLE = "stats"


def run_parse_simulations(database_file: str, simulation_file: str, timepoint: float) -> None:
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
    database.create_table(SIMULATION_TABLE, simulation)

    print(database)
    print(simulation)

    for timepoint in timepoints:
        simulation_df = simulation.parse_timepoint(timepoint)
        database.add_dataframe(SIMULATION_TABLE, simulation_df)
        

def run_calculate_analysis(
    database_file: str,
    simulation_file: str,
    feature_name: str,
    sample_shape: str,
    timepoint: float,
    sample_radius: int,
    needle_direction: int,
    sample_center: tuple,

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
    sample_shape : {"needle", "Needle", "punch", "Punch"}
        The shape of the sample.
    sample_radius :
        The radius of the punch samples or the width of the needle samples.
    needle_direction :
        The direction of needle sampling.
    sample_center :
        The center of the punch sample.
    """
    simulation_file = f"{simulation_path}_{seed}.json"

    database = Database(database_path)
    simulation = Simulation(simulation_file)

    sample: Union[SampleNeedle, SamplePunch]
    if sample_shape in ("needle", "Needle"):
        sample = SampleNeedle(simulation.max_radius, sample_radius, needle_direction)
    elif sample_shape in ("punch", "Punch"):
        sample = SamplePunch(simulation.max_radius, sample_radius, tuple(sample_center))
    else:
        raise AttributeError("The sample type provided is not valid.")

    data = database.load_dataframe(SIMULATION_TABLE, simulation.key)

    for timepoint in timepoints:
        analysis = Analysis(
            simulation.key,
            sample,
            timepoint,
            [Simulation.get_feature_object(feature) for feature in features],
        )
        analysis_df = analysis.calculate_features(data, stats=True, info=True)
        database.create_table(STATS_TABLE, stats)
        database.add_dataframe(STATS_TABLE, stats_df)

        print(stats)

    print(database)

