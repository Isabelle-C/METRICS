import unittest
from unittest import mock

import pandas as pd

from metrics.analysis.analysis import Analysis


class TestAnalysis(unittest.TestCase):
    @mock.patch("metrics.analysis.analysis.SamplePunch")
    @mock.patch("metrics.analysis.analysis.ContinuousFeature")
    def test_calculate_feature_stats_True_returns_continuous_feature_data(
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

        def side_effect(*args, **kwargs):
            if continuous_feature_mock.write_feature_data.call_count == 1:
                return [[key, 0, timepoint, timepoint, "key", feature_name, None, 1.0]]

            elif continuous_feature_mock.write_feature_data.call_count == 2:
                return [[key, 1, timepoint, timepoint, "key", feature_name, None, 1.0]]

        # Set the side effect function on the mock
        continuous_feature_mock.write_feature_data.side_effect = side_effect
        continuous_feature_mock.name = feature_name

        analysis = Analysis(key, punch_sample_mock, timepoint, continuous_feature_mock)

        returned_df = analysis.calculate_feature(
            data, continuous_feature_mock, stats=True, info=False
        )

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

    @mock.patch("metrics.analysis.analysis.SamplePunch")
    @mock.patch("metrics.analysis.analysis.ContinuousFeature")
    def test_calculate_feature_info_True_returns_continuous_feature_data(
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

        def side_effect(*args, **kwargs):
            if continuous_feature_mock.write_feature_data.call_count == 1:
                return [[key, 0, timepoint, timepoint, "key", feature_name, None, 1.0]]

            elif continuous_feature_mock.write_feature_data.call_count == 2:
                return [[key, 1, timepoint, timepoint, "key", feature_name, None, 1.0]]

        # Set the side effect function on the mock
        continuous_feature_mock.write_feature_data.side_effect = side_effect
        continuous_feature_mock.name = feature_name

        analysis = Analysis(key, punch_sample_mock, timepoint, continuous_feature_mock)

        returned_df = analysis.calculate_feature(
            data, continuous_feature_mock, stats=False, info=True
        )

        expected_dict = {
            "key": [key] * 2,
            "seed": [0, 1],
            "tumor_time": [timepoint] * 2,
            "sample_time": [timepoint] * 2,
            "sample_key": ["key"] * 2,
            "feature": [feature_name] * 2,
            "category": [None] * 2,
            "divergence": [1.0] * 2,
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

    @mock.patch("metrics.analysis.analysis.SamplePunch")
    @mock.patch("metrics.analysis.analysis.ContinuousFeature")
    def test_calculate_feature_stats_info_returns_continuous_feature_data(
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

        def side_effect(*args, **kwargs):
            if continuous_feature_mock.write_feature_data.call_count == 1:
                return [[key, 0, timepoint, timepoint, "key", feature_name, None, 1.0, 1.0]]

            elif continuous_feature_mock.write_feature_data.call_count == 2:
                return [[key, 1, timepoint, timepoint, "key", feature_name, None, 1.0, 1.0]]

        # Set the side effect function on the mock
        continuous_feature_mock.write_feature_data.side_effect = side_effect
        continuous_feature_mock.name = feature_name

        analysis = Analysis(key, punch_sample_mock, timepoint, continuous_feature_mock)

        returned_df = analysis.calculate_feature(
            data, continuous_feature_mock, stats=True, info=True
        )

        expected_dict = {
            "key": [key] * 2,
            "seed": [0, 1],
            "tumor_time": [timepoint] * 2,
            "sample_time": [timepoint] * 2,
            "sample_key": ["key"] * 2,
            "feature": [feature_name] * 2,
            "category": [None] * 2,
            "pvalue": [1.0] * 2,
            "divergence": [1.0] * 2,
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

    @mock.patch("metrics.analysis.analysis.SampleNeedle")
    @mock.patch("metrics.analysis.analysis.DiscreteFeature")
    def test_calculate_feature_stats_True_returns_discrete_feature_data(
        self, discrete_feature_mock, needle_sample_mock
    ):
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

        def side_effect(*args, **kwargs):
            if discrete_feature_mock.write_feature_data.call_count == 1:
                return [
                    [key, 0, timepoint, timepoint, "key", feature_name, "0", 1.0],
                    [key, 0, timepoint, timepoint, "key", feature_name, "1", 2.0],
                ]
            elif discrete_feature_mock.write_feature_data.call_count == 2:
                return [
                    [key, 1, timepoint, timepoint, "key", feature_name, "0", 1.0],
                    [key, 1, timepoint, timepoint, "key", feature_name, "1", 2.0],
                ]

        # Set the side effect function on the mock
        discrete_feature_mock.write_feature_data.side_effect = side_effect

        discrete_feature_mock.name = feature_name

        analysis = Analysis(key, needle_sample_mock, timepoint, discrete_feature_mock)

        returned_df = analysis.calculate_feature(
            data, discrete_feature_mock, stats=True, info=False
        )

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

    @mock.patch("metrics.analysis.analysis.SampleNeedle")
    @mock.patch("metrics.analysis.analysis.DiscreteFeature")
    def test_calculate_feature_info_True_returns_discrete_feature_data(
        self, discrete_feature_mock, needle_sample_mock
    ):
        timepoint = 1.0
        key = "SIMULATION_FILE"
        feature_name = "population"

        data_dict = {
            "key": [key] * 9,
            "seed": [0, 0, 0, 0, 0, 0, 0, 0, 0],
            "time": [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 2.0, 2.0, 2.0],
            feature_name: ["0", "0", "0", "1", "1", "1", "0", "0", "0"],
        }
        data = pd.DataFrame(data_dict)

        sample_data_dict = {
            "key": [key] * 4,
            "seed": [
                0,
                0,
                0,
                0,
            ],
            "time": [timepoint] * 4,
            feature_name: ["0", "0", "1", "1"],
        }
        sample_data = pd.DataFrame(sample_data_dict)

        needle_sample_mock.sample_data.return_value = sample_data
        needle_sample_mock.get_sample_key.return_value = "key"

        discrete_feature_mock.write_feature_data.return_value = [
            [key, 0, timepoint, timepoint, "key", feature_name, "0", 1.0],
            [key, 0, timepoint, timepoint, "key", feature_name, "1", 2.0],
        ]

        discrete_feature_mock.name = feature_name

        analysis = Analysis(key, needle_sample_mock, timepoint, discrete_feature_mock)

        returned_df = analysis.calculate_feature(
            data, discrete_feature_mock, stats=False, info=True
        )

        expected_dict = {
            "key": [key] * 2,
            "seed": [0, 0],
            "tumor_time": [timepoint] * 2,
            "sample_time": [timepoint] * 2,
            "sample_key": ["key"] * 2,
            "feature": [feature_name] * 2,
            "category": ["0", "1"],
            "divergence": [1.0, 2.0],
        }
        expected_df = pd.DataFrame(expected_dict)

        self.assertTrue(expected_df.equals(returned_df))

    @mock.patch("metrics.analysis.analysis.SampleNeedle")
    @mock.patch("metrics.analysis.analysis.DiscreteFeature")
    def test_calculate_feature_info_stats_returns_discrete_feature_data(
        self, discrete_feature_mock, needle_sample_mock
    ):
        timepoint = 1.0
        key = "SIMULATION_FILE"
        feature_name = "population"

        data_dict = {
            "key": [key] * 9,
            "seed": [0, 0, 0, 0, 0, 0, 0, 0, 0],
            "time": [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 2.0, 2.0, 2.0],
            feature_name: ["0", "0", "0", "1", "1", "1", "0", "0", "0"],
        }
        data = pd.DataFrame(data_dict)

        sample_data_dict = {
            "key": [key] * 4,
            "seed": [
                0,
                0,
                0,
                0,
            ],
            "time": [timepoint] * 4,
            feature_name: ["0", "0", "1", "1"],
        }
        sample_data = pd.DataFrame(sample_data_dict)

        needle_sample_mock.sample_data.return_value = sample_data
        needle_sample_mock.get_sample_key.return_value = "key"

        discrete_feature_mock.write_feature_data.return_value = [
            [key, 0, timepoint, timepoint, "key", feature_name, "0", 1.0, 1.0],
            [key, 0, timepoint, timepoint, "key", feature_name, "1", 2.0, 2.0],
        ]

        discrete_feature_mock.name = feature_name

        analysis = Analysis(key, needle_sample_mock, timepoint, discrete_feature_mock)

        returned_df = analysis.calculate_feature(data, discrete_feature_mock, stats=True, info=True)

        expected_dict = {
            "key": [key] * 2,
            "seed": [0, 0],
            "tumor_time": [timepoint] * 2,
            "sample_time": [timepoint] * 2,
            "sample_key": ["key"] * 2,
            "feature": [feature_name] * 2,
            "category": ["0", "1"],
            "pvalue": [1.0, 2.0],
            "divergence": [1.0, 2.0],
        }
        expected_df = pd.DataFrame(expected_dict)

        self.assertTrue(expected_df.equals(returned_df))
