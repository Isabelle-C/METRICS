import unittest
from unittest import mock
from unittest.mock import Mock

import pandas as pd

from metrics.analysis.analysis import Analysis
from metrics.analysis.simulation import Simulation
from metrics.feature.continuous_feature import ContinuousFeature
from metrics.feature.discrete_feature import DiscreteFeature
from metrics.sample.sample_needle import SampleNeedle
from metrics.sample.sample_punch import SamplePunch


class TestAnalysis(unittest.TestCase):
    @mock.patch("metrics.analysis.analysis.Experiment")
    def test_calculate_feature_returns_continuous_feature_data(self, experiment_mock):
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

        punch_sample_mock = Mock(spec=SamplePunch)
        punch_sample_mock.sample_data.return_value = sample_data
        punch_sample_mock.get_sample_key.return_value = "key"

        continuous_feature_mock = Mock(spec=ContinuousFeature)

        def side_effect(*args, **kwargs):
            if continuous_feature_mock.write_feature_data.call_count == 1:
                return [
                    [
                        "comparison_key",
                        key,
                        0,
                        timepoint,
                        timepoint,
                        "key",
                        "key",
                        feature_name,
                        None,
                        1.0,
                        1.0,
                    ]
                ]

            elif continuous_feature_mock.write_feature_data.call_count == 2:
                return [
                    [
                        "comparison_key",
                        key,
                        1,
                        timepoint,
                        timepoint,
                        "key",
                        "key",
                        feature_name,
                        None,
                        1.0,
                        1.0,
                    ]
                ]

        # Set the side effect function on the mock

        continuous_feature_mock.write_feature_data.side_effect = side_effect
        continuous_feature_mock.name = feature_name

        simulation_mock = Mock(spec=Simulation)
        experiment_mock.create_experiment_dict.return_value = {
            "reference": simulation_mock,
            "observation": punch_sample_mock,
        }

        analysis = Analysis(key, experiment_mock, timepoint, timepoint, continuous_feature_mock)

        returned_df = analysis.calculate_feature(data, continuous_feature_mock)

        expected_dict = {
            "comparison_group": ["comparison_key", "comparison_key"],
            "key": [key] * 2,
            "seed": [0, 1],
            "reference_time": [timepoint] * 2,
            "obervation_time": [timepoint] * 2,
            "reference_key": ["key"] * 2,
            "obervation_key": ["key"] * 2,
            "feature": [feature_name] * 2,
            "category": [None] * 2,
            "pvalue": [1.0] * 2,
            "divergence": [1.0] * 2,
        }
        expected_df = pd.DataFrame(expected_dict)

        self.assertTrue(expected_df.equals(returned_df))
        compare_feature_calls = continuous_feature_mock.compare_feature_info.call_args_list

        for seed, call in enumerate(compare_feature_calls):
            (sample_arg, tumor_arg), _ = call

            self.assertTrue(sample_data[(sample_data["seed"] == seed)].equals(sample_arg))

            self.assertTrue(
                data[(data["time"] == timepoint) & (data["seed"] == seed)].equals(tumor_arg)
            )

    @mock.patch("metrics.analysis.analysis.Experiment")
    def test_calculate_feature_returns_discrete_feature_data(self, experiment_mock):
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

        needle_sample_mock = Mock(spec=SampleNeedle)
        needle_sample_mock.sample_data.return_value = sample_data
        needle_sample_mock.get_sample_key.return_value = "key"

        discrete_feature_mock = Mock(spec=DiscreteFeature)
        discrete_feature_mock.write_feature_data.return_value = [
            [
                "comparison_key",
                key,
                0,
                timepoint,
                timepoint,
                "key",
                "key",
                feature_name,
                "0",
                1.0,
                1.0,
            ],
            [
                "comparison_key",
                key,
                0,
                timepoint,
                timepoint,
                "key",
                "key",
                feature_name,
                "1",
                2.0,
                2.0,
            ],
        ]

        discrete_feature_mock.name = feature_name

        simulation_mock = Mock(spec=Simulation)
        experiment_mock.create_experiment_dict.return_value = {
            "reference": simulation_mock,
            "observation": needle_sample_mock,
        }

        analysis = Analysis(key, experiment_mock, timepoint, timepoint, discrete_feature_mock)

        returned_df = analysis.calculate_feature(data, discrete_feature_mock)

        expected_dict = {
            "comparison_group": ["comparison_key"] * 2,
            "key": [key] * 2,
            "seed": [0, 0],
            "reference_time": [timepoint] * 2,
            "obervation_time": [timepoint] * 2,
            "reference_key": ["key"] * 2,
            "obervation_key": ["key"] * 2,
            "feature": [feature_name] * 2,
            "category": ["0", "1"],
            "pvalue": [1.0, 2.0],
            "divergence": [1.0, 2.0],
        }
        expected_df = pd.DataFrame(expected_dict)

        self.assertTrue(expected_df.equals(returned_df))
