import unittest
import math

import pandas as pd

from metrics.feature.discrete_feature import DiscreteFeature


class TestDiscreteFeature(unittest.TestCase):
    def test_compare_feature_single_category_given_data_returns_probability(self):
        feature_name = "feature_name"
        affinity = "numeric"
        is_null = True
        categories = ["0"]
        discrete_feature = DiscreteFeature(feature_name, affinity, is_null, categories)

        sample_data = ["0", "0", "0", "1", "1", "1"]
        tumor_data = ["0", "0", "0", "0", "1", "1", "1", "1", "1", "1"]

        expected_probability = {"0": 0.38095}

        sample_dataframe = pd.DataFrame({feature_name: sample_data})
        tumor_dataframe = pd.DataFrame({feature_name: tumor_data})

        returned_probability = discrete_feature.compare_feature(sample_dataframe, tumor_dataframe)

        self.assertAlmostEqual(expected_probability["0"], returned_probability["0"], places=5)

    def test_compare_feature_multiple_category_given_data_returns_probabilities(self):
        feature_name = "feature_name"
        affinity = "numeric"
        is_null = True
        categories = ["0", "1"]
        discrete_feature = DiscreteFeature(feature_name, affinity, is_null, categories)

        sample_data = ["0", "0", "0", "1", "1", "2"]
        tumor_data = ["0", "0", "0", "0", "1", "1", "1", "2", "2", "2"]

        expected_probability = {"0": 0.38095, "1": 0.50000}

        sample_dataframe = pd.DataFrame({feature_name: sample_data})
        tumor_dataframe = pd.DataFrame({feature_name: tumor_data})

        returned_probability = discrete_feature.compare_feature(sample_dataframe, tumor_dataframe)

        self.assertAlmostEqual(expected_probability["0"], returned_probability["0"], places=5)
        self.assertAlmostEqual(expected_probability["1"], returned_probability["1"], places=5)

    def test_compare_feature_feature_not_in_sample_returns_nan(self):
        feature_name = "feature_name"
        affinity = "numeric"
        is_null = True
        categories = ["0"]
        discrete_feature = DiscreteFeature(feature_name, affinity, is_null, categories)

        sample_dataframe = pd.DataFrame({"other_feature": []})
        tumor_dataframe = pd.DataFrame({feature_name: []})

        returned_nan = discrete_feature.compare_feature(sample_dataframe, tumor_dataframe)

        self.assertTrue(math.isnan(returned_nan["0"]))

    def test_compare_feature_feature_not_in_tumor_returns_nan(self):
        feature_name = "feature_name"
        affinity = "numeric"
        is_null = True
        categories = ["0"]
        discrete_feature = DiscreteFeature(feature_name, affinity, is_null, categories)

        sample_dataframe = pd.DataFrame({feature_name: []})
        tumor_dataframe = pd.DataFrame({"other_feature": []})

        returned_nan = discrete_feature.compare_feature(sample_dataframe, tumor_dataframe)

        self.assertTrue(math.isnan(returned_nan["0"]))


if __name__ == "__main__":
    unittest.main()
