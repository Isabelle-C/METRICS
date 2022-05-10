import unittest
import math

import pandas as pd

from abmbiopsy.discrete_feature import DiscreteFeature


class TestDiscreteFeature(unittest.TestCase):
    def test_compare_feature_given_data_returns_probability(self):
        feature_name = "feature_name"
        affinity = "numeric"
        is_null = True
        category = "a"
        discrete_feature = DiscreteFeature(feature_name, affinity, is_null, category)

        sample_data = ["a", "a", "a", "b", "b", "c"]
        tumor_data = ["a", "a", "a", "a", "b", "b", "b", "c", "c", "c"]

        expected_probability = 0.38095

        sample_dataframe = pd.DataFrame({feature_name: sample_data})
        tumor_dataframe = pd.DataFrame({feature_name: tumor_data})

        returned_probability = discrete_feature.compare_feature(sample_dataframe, tumor_dataframe)

        self.assertAlmostEqual(expected_probability, returned_probability, places=5)

    def test_compare_feature_feature_not_in_sample_returns_nan(self):
        feature_name = "feature_name"
        affinity = "numeric"
        is_null = True
        category = "a"
        discrete_feature = DiscreteFeature(feature_name, affinity, is_null, category)

        sample_dataframe = pd.DataFrame({"other_feature": []})
        tumor_dataframe = pd.DataFrame({feature_name: []})

        returned_nan = discrete_feature.compare_feature(sample_dataframe, tumor_dataframe)

        self.assertEqual(True, math.isnan(returned_nan))

    def test_compare_feature_feature_not_in_tumor_returns_nan(self):
        feature_name = "feature_name"
        affinity = "numeric"
        is_null = True
        category = "a"
        discrete_feature = DiscreteFeature(feature_name, affinity, is_null, category)

        sample_dataframe = pd.DataFrame({feature_name: []})
        tumor_dataframe = pd.DataFrame({"other_feature": []})

        returned_nan = discrete_feature.compare_feature(sample_dataframe, tumor_dataframe)

        self.assertEqual(True, math.isnan(returned_nan))


if __name__ == "__main__":
    unittest.main()
