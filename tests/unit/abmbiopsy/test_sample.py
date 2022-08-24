import unittest

from src.abmbiopsy.sample import Sample


class TestSample(unittest.TestCase):
    def test_select_punch_sample_location_returns_locations(self):
        sample_shape = "punch"
        tests = {
            1: [(0, 0, 0)],
            2: [(0, 0, 0), (0, 1, -1), (0, -1, 1), (1, 0, -1), (-1, 0, 1), (-1, 1, 0), (1, -1, 0)],
            3: [
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
        }

        for sample_radius in tests:
            with self.subTest(sample_radius=sample_radius):
                sample = Sample(sample_shape, sample_radius)
                found = sample.select_punch_sample_locations()

                expected = tests[sample_radius]

                self.assertCountEqual(found, expected)

    def test_select_needle_sample_location_returns_locations(self):
        sample_shape = "needle"
        tests = {
            (1, 4): [(0, 0, 0), (0, -1, 1), (0, -2, 2), (0, -3, 3)],
            (3, 3): [
                (0, 0, 0),
                (0, -1, 1),
                (0, -2, 2),
                (-1, -1, 2),
                (-1, 0, 1),
                (1, -2, 1),
                (1, -1, 0),
            ],
            (3, 4): [
                (0, 0, 0),
                (0, -1, 1),
                (0, -2, 2),
                (-1, -1, 2),
                (-1, 0, 1),
                (1, -2, 1),
                (1, -1, 0),
                (0, -3, 3),
                (1, -3, 2),
                (-1, -2, 3),
            ],
        }

        for sample_width, sample_radius in tests:
            with self.subTest(sample_width=sample_width, sample_radius=sample_radius):
                sample = Sample(sample_shape, sample_radius)

                found = sample.select_needle_sample_location(sample_width)
                expected = tests[sample_width, sample_radius]

                self.assertCountEqual(found, expected)

    def test_select_needle_sample_location_raise_ValueError_given_even_width(self):
        sample = Sample("needle", 3)
        sample_width = 2

        with self.assertRaises(ValueError):
            sample.select_needle_sample_location(sample_width)
