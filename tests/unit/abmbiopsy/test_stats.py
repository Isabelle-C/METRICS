import unittest
from unittest import mock

from abmbiopsy.continuous_feature import ContinuousFeature
from abmbiopsy.discrete_feature import DiscreteFeature
from abmbiopsy.feature import Feature
from abmbiopsy.stats import Stats


class TestStats(unittest.TestCase):
    @mock.patch("abmbiopsy.stats.Simulation")
    def test_get_feature_object_given_nonexistent_feature_raises_value_error(self, simulation_mock):
        simulation_mock.get_feature_list.return_value = [Feature("feature_1", "NUMERIC", False)]

        with self.assertRaises(ValueError):
            Stats.get_feature_object("feature_3")

    @mock.patch("abmbiopsy.stats.Simulation")
    def test_get_feature_object_given_invalid_feature_raises_value_error(self, simulation_mock):
        simulation_mock.get_feature_list.return_value = [
            ContinuousFeature("feature_1", "NUMERIC", False),
            Feature("feature_2", "NUMERIC", False),
        ]
        with self.assertRaises(ValueError):
            Stats.get_feature_object("feature_2")

    @mock.patch("abmbiopsy.stats.Simulation")
    def test_get_feature_object_returns_feature(self, simulation_mock):
        expected_feature = ContinuousFeature("feature_1", "NUMERIC", False)

        simulation_mock.get_feature_list.return_value = [expected_feature]

        found_feature = Stats.get_feature_object("feature_1")
        self.assertEqual(expected_feature, found_feature)
