from abmbiopsy.database import Database
from abmbiopsy.simulation import Simulation
from abmbiopsy.sample import Sample
from abmbiopsy.stats import Stats

SIMULATION_TABLE = "simulation"
STATS_TABLE = "stats"


def run_parse_simulations(database_file, simulation_file, timepoint):
    """
    TODO: add docstring
    """
    database = Database(database_file)
    simulation = Simulation(simulation_file)
    print(database)
    print(simulation)

    simulation_df = simulation.parse_timepoint(timepoint)
    database.add_dataframe(SIMULATION_TABLE, simulation_df)


def run_calculate_stats(
    database_file, simulation_key, feature_name, sample_shape, sample_radius, timepoint
):
    """
    TODO: add docstring
    """
    database = Database(database_file)
    sample = Sample(sample_shape, sample_radius)
    stats = Stats(simulation_key, sample, timepoint)
    print(database)
    print(stats)

    data = database.load_dataframe(SIMULATION_TABLE, simulation_key)
    stats_df = stats.calculate_feature(feature_name, data)
    database.add_dataframe(STATS_TABLE, stats_df)
