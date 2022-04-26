import unittest

from abmbiopsy.feature import Feature


class TestFeature(unittest.TestCase):
    def test_init_given_invalid_affinity_raise_typeerror(self):
        name = "feature_name"
        affinity = "invalid_affinity"
        is_null = False
        with self.assertRaises(TypeError):
            Feature(name, affinity, is_null)

    def test_make_query_given_feature_not_null_returns_query(
        self,
    ):
        name = "feature_name"
        affinity = "numeric"
        is_null = False
        feature = Feature(name, affinity, is_null)

        return_string = feature.make_query()
        expected_string = f"{name} {affinity} NOT NULL"
        self.assertEqual(expected_string, return_string)

    def test_make_query_given_feature_is_null_returns_query(
        self,
    ):
        name = "feature_name"
        affinity = "integer"
        is_null = True
        feature = Feature(name, affinity, is_null)

        return_string = feature.make_query()
        expected_string = f"{name} {affinity} "
        self.assertEqual(expected_string, return_string)
