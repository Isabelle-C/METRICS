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
