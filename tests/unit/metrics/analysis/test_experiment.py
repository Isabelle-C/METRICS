import unittest
from unittest import mock
from unittest.mock import Mock

from metrics.analysis.coordinate import Coordinate
from metrics.analysis.analysis import Experiment
from metrics.analysis.simulation import Simulation
from metrics.sample.sample_punch import SamplePunch


class TestExperiment(unittest.TestCase):
    def setUp(self):
        self.comparison = {"reference": "simulation", "observation": "punch_1"}
        self.comparison_group = " | ".join(self.comparison.values())
        self.samples = {
            "punch_1": {"sample_shape": "punch", "sample_radius": 1, "punch_center": [0, 0, 0]}
        }
        self.simulation = Mock(spec=Simulation)
        self.simulation.max_radius = 1

    def test_int_sets_attributes(self):
        experiment = Experiment(self.comparison, self.samples, self.simulation)
        assert experiment.comparison_group == self.comparison_group

    def test_create_experiment_dict(self):
        experiment = Experiment(self.comparison, self.samples, self.simulation)

        expected_dict = {
            "reference": self.simulation,
            "observation": SamplePunch(
                self.simulation.max_radius,
                int(self.samples["punch_1"]["sample_radius"]),
                tuple(self.samples["punch_1"]["punch_center"]),
            ),
        }

        returned_dict = experiment.create_experiment_dict()
        expected_punch = expected_dict["observation"]
        returned_punch = returned_dict["observation"]

        self.assertEqual(expected_dict.keys(), returned_dict.keys())
        self.assertEqual(expected_dict["reference"], returned_dict["reference"])
        self.assertEqual(expected_punch.simulation_radius, returned_punch.simulation_radius)
        self.assertEqual(expected_punch.sample_radius, returned_punch.sample_radius)
        self.assertDictEqual(expected_punch.center.__dict__, returned_punch.center.__dict__)
