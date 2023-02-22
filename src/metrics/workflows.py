from typing import Union

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
    needle_direction :
        The direction of needle sampling.
    sample_center :
        The center of the punch sample.
    """
    database = Database(database_file)
    simulation = Simulation(simulation_file)
    feature = Simulation.get_feature_object(feature_name)

    sample: Union[SampleNeedle, SamplePunch]
    if sample_shape in ("needle", "Needle"):
        sample = SampleNeedle(simulation.max_radius, sample_radius, needle_direction)
    elif sample_shape in ("punch", "Punch"):
        sample = SamplePunch(simulation.max_radius, sample_radius, sample_center)
    else:
        raise AttributeError("The sample type provided is not valid.")

    analysis = Analysis(simulation.key, sample, timepoint, feature)
    print(database)
    print(analysis)

    data = database.load_dataframe(SIMULATION_TABLE, simulation.key)
    analysis_df = analysis.calculate_feature(data, stats=True, info=True)
    database.add_dataframe(ANALYSIS_TABLE, analysis_df)
