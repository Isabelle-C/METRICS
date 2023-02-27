import unittest
import math

import numpy as np
import pandas as pd
from scipy.stats import entropy, kstest, kstwo, gaussian_kde

from metrics.feature.continuous_feature import ContinuousFeature


class TestContinuousFeature(unittest.TestCase):
    def test_compare_feature_stat_given_data_calculates_pvalue(self):
        feature_name = "feature_name"
        affinity = "numeric"
        is_null = True
        continuous_feature = ContinuousFeature(feature_name, affinity, is_null)

        sample_data = [0, 1, 3, 4, 4, 4, 5, 7]
        tumor_data = [0, 1, 2, 2, 4, 6, 6, 7]

        sample_dataframe = pd.DataFrame({feature_name: sample_data})
        tumor_dataframe = pd.DataFrame({feature_name: tumor_data})

        expected_pvalue = kstwo.sf(0.25, n=8)
        returned_pvalue = continuous_feature.compare_feature_stat(sample_dataframe, tumor_dataframe)

        self.assertAlmostEqual(expected_pvalue, returned_pvalue, places=5)

    def test_compare_feature_stat_feature_not_in_sample_returns_nan(self):
        feature_name = "feature_name"
        affinity = "numeric"
        is_null = True
        continuous_feature = ContinuousFeature(feature_name, affinity, is_null)

        sample_dataframe = pd.DataFrame({"other_feature": []})
        tumor_dataframe = pd.DataFrame({feature_name: []})

        returned_nan = continuous_feature.compare_feature_stat(sample_dataframe, tumor_dataframe)
        self.assertTrue(math.isnan(returned_nan))

    def test_compare_feature_stat_feature_not_in_tumor_returns_nan(self):
        feature_name = "feature_name"
        affinity = "numeric"
        is_null = True
        continuous_feature = ContinuousFeature(feature_name, affinity, is_null)

        sample_dataframe = pd.DataFrame({feature_name: []})
        tumor_dataframe = pd.DataFrame({"other_feature": []})

        returned_nan = continuous_feature.compare_feature_stat(sample_dataframe, tumor_dataframe)
        self.assertTrue(math.isnan(returned_nan))

    def test_compare_feature_info(self):
        feature_name = "feature_name"
        affinity = "numeric"
        is_null = True
        continuous_feature = ContinuousFeature(feature_name, affinity, is_null)

        sample_data = [1, 2, 4, 4, 4, 6, 7]
        tumor_data = [1, 2, 2, 4, 6, 6, 7]

        sample_prob, reference_prob = continuous_feature.get_pdfs(
            sample_data,
            tumor_data,
        )

        expected_divergence = entropy(sample_prob, reference_prob)

        sample_dataframe = pd.DataFrame({feature_name: sample_data})
        tumor_dataframe = pd.DataFrame({feature_name: tumor_data})
        returned_divergence = continuous_feature.compare_feature_info(
            sample_dataframe, tumor_dataframe
        )

        self.assertAlmostEqual(expected_divergence, returned_divergence, places=5)

    def test_compare_feature_info_given_unequal_array_length(self):
        feature_name = "feature_name"
        affinity = "numeric"
        is_null = True
        continuous_feature = ContinuousFeature(feature_name, affinity, is_null)

        sample_data = [0.3, 0.1, 0.1]
        tumor_data = [0.3, 0.3, 0.1, 0.1]

        sample_prob, reference_prob = continuous_feature.get_pdfs(sample_data, tumor_data)

        expected_divergence = entropy(sample_prob, reference_prob)

        sample_dataframe = pd.DataFrame({feature_name: sample_data})
        tumor_dataframe = pd.DataFrame({feature_name: tumor_data})
        returned_divergence = continuous_feature.compare_feature_info(
            sample_dataframe, tumor_dataframe
        )

        self.assertAlmostEqual(expected_divergence, returned_divergence, places=5)

    def test_write_feature_data_stats(self):
        feature_name = "feature_name"
        affinity = "numeric"
        is_null = True
        continuous_feature = ContinuousFeature(feature_name, affinity, is_null)

        data_list = ["col1", "col2", "col3"]
        stats = True
        info = False
        timepoint = 1.0
        key = "SIMULATION_FILE"

        simulation_data_dict = {
            "key": [key] * 9,
            "seed": [0, 0, 0, 0, 0, 0, 1, 1, 1],
            "time": [1.0, 1.0, 1.0, 2.0, 2.0, 2.0, 1.0, 1.0, 1.0],
            feature_name: [3001, 2500, 2600, 3002, 2400, 2900, 3050, 2550, 2650],
        }
        simulation_data = pd.DataFrame(simulation_data_dict)

        sample_data_dict = {
            "key": [key] * 4,
            "seed": [0, 0, 1, 1],
            "time": [timepoint] * 4,
            feature_name: [3001, 2500, 3050, 2550],
        }
        sample_data = pd.DataFrame(sample_data_dict)

        output_list = continuous_feature.write_feature_data(
            data_list, stats, info, sample_data, simulation_data
        )

        expected_value = continuous_feature.compare_feature_stat(sample_data, simulation_data)
        expected_list = [
            ["col1", "col2", "col3", None, expected_value],
        ]

        self.assertEqual(output_list, expected_list)

    def test_write_feature_data_info(self):
        feature_name = "feature_name"
        affinity = "numeric"
        is_null = True
        continuous_feature = ContinuousFeature(feature_name, affinity, is_null)

        data_list = ["col1", "col2", "col3"]
        stats = False
        info = True
        timepoint = 1.0
        key = "SIMULATION_FILE"

        simulation_data_dict = {
            "key": [key] * 9,
            "seed": [0, 0, 0, 0, 0, 0, 1, 1, 1],
            "time": [1.0, 1.0, 1.0, 2.0, 2.0, 2.0, 1.0, 1.0, 1.0],
            feature_name: [3001, 2500, 2600, 3002, 2400, 2900, 3050, 2550, 2650],
        }
        simulation_data = pd.DataFrame(simulation_data_dict)

        sample_data_dict = {
            "key": [key] * 4,
            "seed": [0, 0, 1, 1],
            "time": [timepoint] * 4,
            feature_name: [3001, 2500, 3050, 2550],
        }
        sample_data = pd.DataFrame(sample_data_dict)

        output_list = continuous_feature.write_feature_data(
            data_list, stats, info, sample_data, simulation_data
        )

        expected_value = continuous_feature.compare_feature_info(sample_data, simulation_data)
        expected_list = [["col1", "col2", "col3", None, expected_value]]

        self.assertEqual(output_list, expected_list)

    def test_write_feature_data_info_stat(self):
        feature_name = "feature_name"
        affinity = "numeric"
        is_null = True
        continuous_feature = ContinuousFeature(feature_name, affinity, is_null)

        data_list = ["col1", "col2", "col3"]
        stats = True
        info = True
        timepoint = 1.0
        key = "SIMULATION_FILE"

        simulation_data_dict = {
            "key": [key] * 9,
            "seed": [0, 0, 0, 0, 0, 0, 1, 1, 1],
            "time": [1.0, 1.0, 1.0, 2.0, 2.0, 2.0, 1.0, 1.0, 1.0],
            feature_name: [3001, 2500, 2600, 3002, 2400, 2900, 3050, 2550, 2650],
        }
        simulation_data = pd.DataFrame(simulation_data_dict)

        sample_data_dict = {
            "key": [key] * 4,
            "seed": [0, 0, 1, 1],
            "time": [timepoint] * 4,
            feature_name: [3001, 2500, 3050, 2550],
        }
        sample_data = pd.DataFrame(sample_data_dict)

        output_list = continuous_feature.write_feature_data(
            data_list, stats, info, sample_data, simulation_data
        )

        expected_value_info = continuous_feature.compare_feature_info(sample_data, simulation_data)
        expected_value_stats = continuous_feature.compare_feature_stat(sample_data, simulation_data)
        expected_list = [["col1", "col2", "col3", None, expected_value_stats, expected_value_info]]

        self.assertEqual(output_list, expected_list)


if __name__ == "__main__":
    unittest.main()
