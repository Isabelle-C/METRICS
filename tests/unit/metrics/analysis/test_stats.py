import unittest
from unittest import mock

import pandas as pd

from metrics.feature.continuous_feature import ContinuousFeature
from metrics.feature.discrete_feature import DiscreteFeature
from metrics.feature.feature import Feature
from metrics.sample.sample_needle import SampleNeedle
from metrics.sample.sample_punch import SamplePunch
from metrics.analysis.simulation import Simulation
from metrics.analysis.stats import Stats


class TestStats(unittest.TestCase):
    @mock.patch("metrics.analysis.stats.SamplePunch")
    @mock.patch("metrics.analysis.stats.ContinuousFeature")
    def test_calculate_feature_returns_continuous_feature_data(
        self, continuous_feature_mock, punch_sample_mock
    ):
        timepoint = 1.0
        key = "SIMULATION_FILE"
        feature_name = "cycle"

        data_dict = {
            "key": [key] * 9,
            "seed": [0, 0, 0, 0, 0, 0, 1, 1, 1],
            "time": [1.0, 1.0, 1.0, 2.0, 2.0, 2.0, 1.0, 1.0, 1.0],
            feature_name: [3001, 2500, 2600, 3002, 2400, 2900, 3050, 2550, 2650],
        }
        data = pd.DataFrame(data_dict)

        sample_data_dict = {
            "key": [key] * 4,
            "seed": [0, 0, 1, 1],
            "time": [timepoint] * 4,
            feature_name: [3001, 2500, 3050, 2550],
        }
        sample_data = pd.DataFrame(sample_data_dict)

        punch_sample_mock.sample_data.return_value = sample_data
        punch_sample_mock.get_sample_key.return_value = "key"

        continuous_feature_mock.compare_feature.return_value = 1.0
        continuous_feature_mock.name = feature_name

        stats = Stats(key, punch_sample_mock, timepoint, continuous_feature_mock)

        returned_df = stats.calculate_feature(data, continuous_feature_mock)

        expected_dict = {
            "key": [key] * 2,
            "seed": [0, 1],
            "tumor_time": [timepoint] * 2,
            "sample_time": [timepoint] * 2,
            "sample_key": ["key"] * 2,
            "feature": [feature_name] * 2,
            "category": [None] * 2,
            "pvalue": [1.0] * 2,
        }
        expected_df = pd.DataFrame(expected_dict)

        self.assertTrue(expected_df.equals(returned_df))
        compare_feature_calls = continuous_feature_mock.compare_feature.call_args_list

        for seed, call in enumerate(compare_feature_calls):

            (sample_arg, tumor_arg), _ = call

            self.assertTrue(sample_data[(sample_data["seed"] == seed)].equals(sample_arg))

            self.assertTrue(
                data[(data["time"] == timepoint) & (data["seed"] == seed)].equals(tumor_arg)
            )

    @mock.patch("metrics.analysis.stats.SampleNeedle")
    @mock.patch("metrics.analysis.stats.DiscreteFeature")
    def test_calculate_feature_returns_discrete_feature_data(
        self, discrete_feature_mock, needle_sample_mock
    ):
        seed = 0
        timepoint = 1.0
        key = "SIMULATION_FILE"
        feature_name = "population"

        data_dict = {
            "key": [key] * 12,
            "seed": [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1],
            "time": [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 2.0, 2.0, 2.0, 1.0, 1.0, 1.0],
            feature_name: ["0", "0", "0", "1", "1", "1", "0", "0", "0", "0", "0", "0"],
        }
        data = pd.DataFrame(data_dict)

        sample_data_dict = {
            "key": [key] * 6,
            "seed": [0, 0, 0, 0, 1, 1],
            "time": [timepoint] * 6,
            feature_name: ["0", "0", "1", "1", "0", "0"],
        }
        sample_data = pd.DataFrame(sample_data_dict)

        needle_sample_mock.sample_data.return_value = sample_data
        needle_sample_mock.get_sample_key.return_value = "key"

        discrete_feature_mock.compare_feature.return_value = {"0": 1.0, "1": 2.0}
        discrete_feature_mock.name = feature_name

        stats = Stats(key, needle_sample_mock, timepoint, discrete_feature_mock)

        returned_df = stats.calculate_feature(data, discrete_feature_mock)

        expected_dict = {
            "key": [key] * 4,
            "seed": [0, 0, 1, 1],
            "tumor_time": [timepoint] * 4,
            "sample_time": [timepoint] * 4,
            "sample_key": ["key"] * 4,
            "feature": [feature_name] * 4,
            "category": ["0", "1", "0", "1"],
            "pvalue": [1.0, 2.0, 1.0, 2.0],
        }
        expected_df = pd.DataFrame(expected_dict)

        self.assertTrue(expected_df.equals(returned_df))
        compare_feature_calls = discrete_feature_mock.compare_feature.call_args_list

        for seed, call in enumerate(compare_feature_calls):

            (sample_arg, tumor_arg), _ = call

            self.assertTrue(sample_data[(sample_data["seed"] == seed)].equals(sample_arg))

            self.assertTrue(
                data[(data["time"] == timepoint) & (data["seed"] == seed)].equals(tumor_arg)
            )
