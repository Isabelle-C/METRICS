import unittest
import math

import pandas as pd

from abmbiopsy.discrete_feature import DiscreteFeature


class TestDiscreteFeature(unittest.TestCase):
    def test_compare_feature_single_category_given_data_returns_probability(self):
        feature_name = "feature_name"
        affinity = "numeric"
        is_null = True
        categories = ["a"]
        discrete_feature = DiscreteFeature(feature_name, affinity, is_null, categories)

        sample_data = ["a", "a", "a", "b", "b", "b"]
        tumor_data = ["a", "a", "a", "a", "b", "b", "b", "b", "b", "b"]

        expected_probability = {"a": 0.38095}

        sample_dataframe = pd.DataFrame({feature_name: sample_data})
        tumor_dataframe = pd.DataFrame({feature_name: tumor_data})

        returned_probability = discrete_feature.compare_feature(sample_dataframe, tumor_dataframe)

        self.assertAlmostEqual(expected_probability["a"], returned_probability["a"], places=5)

    def test_compare_feature_multiple_category_given_data_returns_probabilities(self):
        feature_name = "feature_name"
        affinity = "numeric"
        is_null = True
        categories = ["a", "b"]
        discrete_feature = DiscreteFeature(feature_name, affinity, is_null, categories)

        sample_data = ["a", "a", "a", "b", "b", "c"]
        tumor_data = ["a", "a", "a", "a", "b", "b", "b", "c", "c", "c"]

        expected_probability = {"a": 0.38095, "b": 0.50000}

        sample_dataframe = pd.DataFrame({feature_name: sample_data})
        tumor_dataframe = pd.DataFrame({feature_name: tumor_data})

        returned_probability = discrete_feature.compare_feature(sample_dataframe, tumor_dataframe)

        self.assertAlmostEqual(expected_probability["a"], returned_probability["a"], places=5)
        self.assertAlmostEqual(expected_probability["b"], returned_probability["b"], places=5)

    def test_compare_feature_feature_not_in_sample_returns_nan(self):
        feature_name = "feature_name"
        affinity = "numeric"
        is_null = True
        categories = ["a"]
        discrete_feature = DiscreteFeature(feature_name, affinity, is_null, categories)

        sample_dataframe = pd.DataFrame({"other_feature": []})
        tumor_dataframe = pd.DataFrame({feature_name: []})

        returned_nan = discrete_feature.compare_feature(sample_dataframe, tumor_dataframe)

        self.assertTrue(math.isnan(returned_nan["a"]))

    def test_compare_feature_feature_not_in_tumor_returns_nan(self):
        feature_name = "feature_name"
        affinity = "numeric"
        is_null = True
        categories = ["a"]
        discrete_feature = DiscreteFeature(feature_name, affinity, is_null, categories)

        sample_dataframe = pd.DataFrame({feature_name: []})
        tumor_dataframe = pd.DataFrame({"other_feature": []})

        returned_nan = discrete_feature.compare_feature(sample_dataframe, tumor_dataframe)

        self.assertTrue(math.isnan(returned_nan["a"]))


if __name__ == "__main__":
    unittest.main()
