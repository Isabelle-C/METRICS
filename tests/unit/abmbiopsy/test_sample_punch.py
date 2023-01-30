import unittest
from unittest import mock

from abmbiopsy.sample_punch import SamplePunch


class TestSamplePunch(unittest.TestCase):
    def test_get_sample_key(self):
        sample_radius = 2
        sample_center = (0, 0, 0)
        sample_punch = SamplePunch(5, sample_radius, sample_center)

        found = sample_punch.get_sample_key()
        expected = "punch-R2-(0, 0, 0)"

        self.assertEqual(found, expected)

    def test_select_sample_locations_raise_valueerror(self):
        with self.assertRaises(ValueError):
            SamplePunch(5, 5, (0, 1, -1))

    @mock.patch("abmbiopsy.sample_punch.warnings")
    def test_select_sample_locations_raise_warning(self, mock_warn):
        SamplePunch(5, 5, (0, 0, 0))
        self.assertTrue(mock_warn.warn.called)

    def test_select_sample_locations(self):
        tests = {
            (1, (0, 0, 0)): [(0, 0, 0)],
            (2, (0, 0, 0)): [
                (0, 0, 0),
                (0, 1, -1),
                (0, -1, 1),
                (1, 0, -1),
                (-1, 0, 1),
                (-1, 1, 0),
                (1, -1, 0),
            ],
            (3, (0, 0, 0)): [
                (0, 0, 0),
                (0, 1, -1),
                (0, -1, 1),
                (1, 0, -1),
                (-1, 0, 1),
                (-1, 1, 0),
                (1, -1, 0),
                (0, -2, 2),
                (1, -2, 1),
                (2, -2, 0),
                (2, -1, -1),
                (2, 0, -2),
                (1, 1, -2),
                (0, 2, -2),
                (-1, 2, -1),
                (-2, 2, 0),
                (-2, 1, 1),
                (-2, 0, 2),
                (-1, -1, 2),
            ],
            (2, (2, -2, 0)): [
                (2, -2, 0),
                (2, -3, 1),
                (3, -3, 0),
                (3, -2, -1),
                (2, -1, -1),
                (1, -1, 0),
                (1, -2, 1),
            ],
            (3, (-1, 1, 0)): [
                (-1, 1, 0),
                (-1, 0, 1),
                (0, 0, 0),
                (0, 1, -1),
                (-1, 2, -1),
                (-2, 2, 0),
                (-2, 1, 1),
                (-1, -1, 2),
                (0, -1, 1),
                (1, -1, 0),
                (1, 0, -1),
                (1, 1, -2),
                (0, 2, -2),
                (-1, 3, -2),
                (-2, 3, -1),
                (-3, 3, 0),
                (-3, 2, 1),
                (-3, 1, 2),
                (-2, 0, 2),
            ],
        }

        for sample_radius, sample_center in tests:
            with self.subTest(sample_radius=sample_radius, sample_center=sample_center):
                sample_punch = SamplePunch(5, sample_radius, sample_center)
                found = sample_punch.select_sample_locations()
                expected = tests[sample_radius, sample_center]
                self.assertCountEqual(found, expected)
