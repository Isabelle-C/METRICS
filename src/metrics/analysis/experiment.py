from typing import Union, Dict

from metrics.analysis.simulation import Simulation
from metrics.sample.sample_needle import SampleNeedle
from metrics.sample.sample_punch import SamplePunch


class Experiment:
    """
    Workflow for creating a dictionary of objects for analysis.

    Attributes
    ----------
    comparison : dict
        The comparison to perform analysis on.
    comparison_group : str
        The names of objects compared.
    samples : Dict[str, dict]
        Information about sample parameters.
    simulation : Simulation
        Simulation object.
    """

    def __init__(self, comparison: dict, samples: Dict[str, dict], simulation: Simulation):
        self.comparison = comparison
        self.comparison_group = " | ".join(comparison.values())
        self.samples = samples
        self.simulation = simulation

    def create_experiment_dict(self) -> dict:
        """
        Create sample objects.

        Returns
        -------
        object_dict : Dict[str,Union[Simulation, SampleNeedle, SamplePunch]]
            The dictionary with objects for comparison.
        """
        sample: Union[SampleNeedle, SamplePunch]
        object_dict: dict = {}

        for key, comparison_name in self.comparison.items():
            if comparison_name in ("simulation", "Simulation"):
                object_dict[key] = self.simulation
            else:
                sample_parameters = self.samples[comparison_name]
                sample_shape = sample_parameters["sample_shape"]

                if sample_shape in ("needle", "Needle"):
                    sample = SampleNeedle(
                        self.simulation.max_radius,
                        sample_parameters["sample_radius"],
                        sample_parameters["needle_direction"],
                    )
                    object_dict[key] = sample

                elif sample_shape in ("punch", "Punch"):
                    sample = SamplePunch(
                        self.simulation.max_radius,
                        int(sample_parameters["sample_radius"]),
                        tuple(sample_parameters["punch_center"]),
                    )
                    object_dict[key] = sample
                else:
                    raise AttributeError("The sample type provided is not valid.")
        return object_dict
