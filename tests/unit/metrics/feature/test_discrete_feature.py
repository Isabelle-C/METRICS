import unittest
import math

import pandas as pd

from metrics.feature.discrete_feature import DiscreteFeature


class TestDiscreteFeature(unittest.TestCase):
    def test_compare_feature_stat_single_category_given_data_returns_probability(self):
        feature_name = "feature_name"
        affinity = "numeric"
        is_null = True
        discrete_feature = DiscreteFeature(feature_name, affinity, is_null)

        sample_data = ["0", "0", "0", "1", "1", "1"]
        tumor_data = ["0", "0", "0", "0", "1", "1", "1", "1", "1", "1"]

        expected_probability = {"0": 0.38095}

        sample_dataframe = pd.DataFrame({feature_name: sample_data})
        tumor_dataframe = pd.DataFrame({feature_name: tumor_data})

        returned_probability = discrete_feature.compare_feature_stat(
            sample_dataframe, tumor_dataframe
        )

        self.assertAlmostEqual(expected_probability["0"], returned_probability["0"], places=5)

    def test_compare_feature_stat_multiple_category_given_data_returns_probabilities(self):
        feature_name = "feature_name"
        affinity = "numeric"
        is_null = True
        discrete_feature = DiscreteFeature(feature_name, affinity, is_null)

        sample_data = ["0", "0", "0", "1", "1", "2"]
        tumor_data = ["0", "0", "0", "0", "1", "1", "1", "2", "2", "2"]

        expected_probability = {"0": 0.38095, "1": 0.50000}

        sample_dataframe = pd.DataFrame({feature_name: sample_data})
        tumor_dataframe = pd.DataFrame({feature_name: tumor_data})

        returned_probability = discrete_feature.compare_feature_stat(
            sample_dataframe, tumor_dataframe
        )

        self.assertAlmostEqual(expected_probability["0"], returned_probability["0"], places=5)
        self.assertAlmostEqual(expected_probability["1"], returned_probability["1"], places=5)

    def test_compare_feature_stat_feature_not_in_sample_returns_nan(self):
        feature_name = "feature_name"
        affinity = "numeric"
        is_null = True
        discrete_feature = DiscreteFeature(feature_name, affinity, is_null)

        sample_dataframe = pd.DataFrame({"other_feature": []})
        tumor_dataframe = pd.DataFrame({feature_name: []})

        returned_nan = discrete_feature.compare_feature_stat(sample_dataframe, tumor_dataframe)

        self.assertTrue(math.isnan(returned_nan))

    def test_compare_feature_stat_feature_not_in_tumor_returns_nan(self):
        feature_name = "feature_name"
        affinity = "numeric"
        is_null = True
        discrete_feature = DiscreteFeature(feature_name, affinity, is_null)

        sample_dataframe = pd.DataFrame({feature_name: []})
        tumor_dataframe = pd.DataFrame({"other_feature": []})

        returned_nan = discrete_feature.compare_feature_stat(sample_dataframe, tumor_dataframe)

        self.assertTrue(math.isnan(returned_nan))

    def test_compare_feature_info_feature_not_in_tumor_returns_nan(self):
        feature_name = "feature_name"
        affinity = "numeric"
        is_null = True
        discrete_feature = DiscreteFeature(feature_name, affinity, is_null)

        sample_dataframe = pd.DataFrame({"other_feature": []})
        tumor_dataframe = pd.DataFrame({feature_name: []})

        returned_nan = discrete_feature.compare_feature_info(sample_dataframe, tumor_dataframe)

        self.assertTrue(math.isnan(returned_nan))

    def test_compare_feature_info_single_category_given_data_returns_kl_divergence(self):
        feature_name = "feature_name"
        affinity = "numeric"
        is_null = True
        discrete_feature = DiscreteFeature(feature_name, affinity, is_null)

        sample_data = [0, 0, 0, 1, 1, 1]
        tumor_data = [0, 0, 0, 0, 1, 1, 1, 1, 1, 1]

        x = [sample_data.count(0) / len(sample_data), sample_data.count(1) / len(sample_data)]
        y = [tumor_data.count(0) / len(tumor_data), tumor_data.count(1) / len(tumor_data)]

        expected_probability = sum([x[i] * math.log(x[i] / y[i]) for i in range(len(x))])

        sample_dataframe = pd.DataFrame({feature_name: sample_data})
        tumor_dataframe = pd.DataFrame({feature_name: tumor_data})

        returned_probability = discrete_feature.compare_feature_info(
            sample_dataframe, tumor_dataframe
        )

        self.assertAlmostEqual(expected_probability, returned_probability, places=5)

    def test_write_feature_data_info_stat(self):
        feature_name = "population"
        affinity = "numeric"
        is_null = True
        discrete_feature = DiscreteFeature(feature_name, affinity, is_null)

        data_list = ["col1", "col2", "col3"]
        timepoint = 1.0
        key = "SIMULATION_FILE"

        sample_data_dict = {
            "key": [key] * 4,
            "seed": [0, 0, 0, 0],
            "time": [timepoint] * 4,
            feature_name: ["0", "0", "1", "1"],
        }
        sample_data = pd.DataFrame(sample_data_dict)

        simulation_data_dict = {
            "key": [key] * 9,
            "seed": [0, 0, 0, 0, 0, 0, 0, 0, 0],
            "time": [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 2.0, 2.0, 2.0],
            feature_name: ["0", "0", "0", "1", "1", "1", "0", "0", "0"],
        }
        simulation_data = pd.DataFrame(simulation_data_dict)

        output_list = discrete_feature.write_feature_data(data_list, sample_data, simulation_data)

        expected_value_info = discrete_feature.compare_feature_info(sample_data, simulation_data)
        expected_value_stats = discrete_feature.compare_feature_stat(sample_data, simulation_data)
        expected_list = [
            ["col1", "col2", "col3", "0", expected_value_stats["0"], expected_value_info],
            ["col1", "col2", "col3", "1", expected_value_stats["1"], expected_value_info],
        ]

        self.assertEqual(output_list, expected_list)


if __name__ == "__main__":
    unittest.main()
