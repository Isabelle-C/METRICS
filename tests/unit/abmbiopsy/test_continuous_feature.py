import unittest
import math

import pandas as pd
from scipy.stats import kstwo

from abmbiopsy.continuous_feature import ContinuousFeature


class TestContinuousFeature(unittest.TestCase):
    def test_compare_feature_given_data_calculates_pvalue(self):
        feature_name = "feature_name"
        affinity = "numeric"
        is_null = True
        continuous_feature = ContinuousFeature(feature_name, affinity, is_null)

        sample_data = [0, 1, 3, 4, 4, 4, 5, 7]
        tumor_data = [0, 1, 2, 2, 4, 6, 6, 7]

        sample_dataframe = pd.DataFrame({feature_name: sample_data})
        tumor_dataframe = pd.DataFrame({feature_name: tumor_data})

        expected_pvalue = kstwo.sf(0.25, n=8)
        returned_pvalue = continuous_feature.compare_feature(sample_dataframe, tumor_dataframe)

        self.assertAlmostEqual(expected_pvalue, returned_pvalue, places=5)

    def test_compare_feature_feature_not_in_sample_returns_nan(self):
        feature_name = "feature_name"
        affinity = "numeric"
        is_null = True
        continuous_feature = ContinuousFeature(feature_name, affinity, is_null)

        sample_dataframe = pd.DataFrame({"other_feature": []})
        tumor_dataframe = pd.DataFrame({feature_name: []})

        returned_nan = continuous_feature.compare_feature(sample_dataframe, tumor_dataframe)
        self.assertTrue(math.isnan(returned_nan))

    def test_compare_feature_feature_not_in_tumor_returns_nan(self):
        feature_name = "feature_name"
        affinity = "numeric"
        is_null = True
        continuous_feature = ContinuousFeature(feature_name, affinity, is_null)

        sample_dataframe = pd.DataFrame({feature_name: []})
        tumor_dataframe = pd.DataFrame({"other_feature": []})

        returned_nan = continuous_feature.compare_feature(sample_dataframe, tumor_dataframe)
        self.assertTrue(math.isnan(returned_nan))


if __name__ == "__main__":
    unittest.main()
