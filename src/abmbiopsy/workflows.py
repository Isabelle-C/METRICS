from typing import Union

from abmbiopsy.database import Database
from abmbiopsy.simulation import Simulation
from abmbiopsy.sample_needle import SampleNeedle
from abmbiopsy.sample_punch import SamplePunch
from abmbiopsy.stats import Stats

SIMULATION_TABLE = "simulation"
STATS_TABLE = "stats"


def run_parse_simulations(database_file: str, simulation_file: str, timepoint: float) -> None:
    """
    Parse the simulation and write data into databse file.

    Parameters
    ----------
    database_file :
        File path to the database file.
    simulation_file :
        File path to the simulation file.
    timepoint :
        The timepoint to parse the simulation data.
    """
    database = Database(database_file)
    simulation = Simulation(simulation_file)
    print(database)
    print(simulation)

    simulation_df = simulation.parse_timepoint(timepoint)
    database.add_dataframe(SIMULATION_TABLE, simulation_df)


def run_calculate_stats(
    database_file: str,
    simulation_file: str,
    feature_name: str,
    sample_shape: str,
    timepoint: float,
    sample_radius: int,
) -> None:
    """
    Run the statistical test on data with the specified feature and sampling method.

    Parameters
    ----------
    database_file :
        File path to the database file.
    simulation_file :
        File path to the simulation file.
    feature_name :
        The name of the feature.
    sample_shape : {"needle", "Needle", "punch", "Punch"}
        The shape of the sample.
    timepoint :
        The timepoint to perform statistical test.
    sample_radius :
        The radius of the punch samples or the width of the needle samples.
    """
    database = Database(database_file)
    simulation = Simulation(simulation_file)
    feature = Simulation.get_feature_object(feature_name)

    sample: Union[SampleNeedle, SamplePunch]
    if sample_shape in ("needle", "Needle"):
        sample = SampleNeedle(simulation.max_radius, sample_radius)
    elif sample_shape in ("punch", "Punch"):
        sample = SamplePunch(sample_radius)
    else:
        raise AttributeError("The sample type provided is not valid.")

    stats = Stats(simulation.key, sample, timepoint, feature)
    print(database)
    print(stats)

    data = database.load_dataframe(SIMULATION_TABLE, simulation.key)
    stats_df = stats.calculate_feature(data)
    database.add_dataframe(STATS_TABLE, stats_df)
