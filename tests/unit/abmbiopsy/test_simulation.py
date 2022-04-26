import unittest

from abmbiopsy.feature import Feature
from abmbiopsy.simulation import Simulation


class TestSimulation(unittest.TestCase):
    def test_get_feature_list_returns_list(self):
        output = Simulation.get_feature_list()
        self.assertIsInstance(output, list)

    def test_get_feature_list_returns_list_of_feature_objects(self):
        output = Simulation.get_feature_list()
        for i in output:
            self.assertIsInstance(i, Feature)
