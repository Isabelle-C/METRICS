import unittest

from src.abmbiopsy.sample_needle import SampleNeedle


class TestSampleNeedle(unittest.TestCase):
    def test_select_sample_locations_given_odd_width_returns_locations(self):
        tests = {
            (4, 1): [
                (0, 0, 0),
                (0, -1, 1),
                (0, -2, 2),
                (0, -3, 3),
            ],
            (3, 3): [
                (0, 0, 0),
                (0, -1, 1),
                (0, -2, 2),
                (-1, -1, 2),
                (-1, 0, 1),
                (1, -2, 1),
                (1, -1, 0),
            ],
            (4, 3): [
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

        for simulation_radius, sample_width in tests:
            with self.subTest(simulation_radius=simulation_radius, sample_width=sample_width):
                sample_needle = SampleNeedle(simulation_radius, sample_width)

                found = sample_needle.select_sample_locations()
                expected = tests[(simulation_radius, sample_width)]

                self.assertCountEqual(found, expected)

    def test_select_sample_locations_given_even_width_raises_value_error(self):
        simulation_radius = 3
        sample_width = 2
        sample_needle = SampleNeedle(simulation_radius, sample_width)

        with self.assertRaises(ValueError):
            sample_needle.select_sample_locations()
