import unittest

from src.abmbiopsy.sample_needle import SampleNeedle


class TestSampleNeedle(unittest.TestCase):
    def test_given_invalid_direction_raise_value_error(self):
        with self.assertRaises(ValueError):
            SampleNeedle(1, 3, 7)

    def test_get_sample_key(self):
        simulation_radius = 3
        sample_width = 2
        direction = 1
        sample_needle = SampleNeedle(simulation_radius, sample_width, direction)

        found = sample_needle.get_sample_key()
        expected = f"needle-R3-W2-D1"

        self.assertEqual(found, expected)

    def test_select_sample_locations_given_odd_width_returns_locations(self):
        tests = {
            (4, 1, 1): [
                (0, 0, 0),
                (0, -1, 1),
                (0, -2, 2),
                (0, -3, 3),
            ],
            (3, 3, 1): [
                (0, 0, 0),
                (0, -1, 1),
                (0, -2, 2),
                (-1, -1, 2),
                (-1, 0, 1),
                (1, -2, 1),
                (1, -1, 0),
            ],
            (4, 3, 1): [
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
            (2, 3, 2): [(0, 0, 0), (1, -1, 0), (1, 0, -1), (0, 1, -1)],
            (3, 1, 2): [(0, 0, 0), (1, 0, -1), (2, 0, -2)],
            (3, 3, 2): [
                (0, 0, 0),
                (1, -1, 0),
                (1, 0, -1),
                (0, 1, -1),
                (2, -1, -1),
                (2, 0, -2),
                (1, 1, -2),
            ],
            (3, 1, 3): [
                (-2, 2, 0),
                (-1, 1, 0),
                (0, 0, 0),
            ],
            (3, 3, 3): [
                (0, 0, 0),
                (-1, 0, 1),
                (0, 1, -1),
                (-2, 1, 1),
                (-1, 1, 0),
                (-1, 2, -1),
                (-2, 2, 0),
            ],
            (4, 3, 3): [
                (0, 0, 0),
                (-1, 0, 1),
                (0, 1, -1),
                (-2, 1, 1),
                (-1, 1, 0),
                (-1, 2, -1),
                (-2, 2, 0),
                (-3, 2, 1),
                (-3, 3, 0),
                (-2, 3, -1),
            ],
            (4, 3, 4): [
                (2, -3, 1),
                (1, -2, 1),
                (0, -1, 1),
                (3, -3, 0),
                (2, -2, 0),
                (1, -1, 0),
                (0, 0, 0),
                (3, -2, -1),
                (2, -1, -1),
                (1, 0, -1),
            ],
            (3, 3, 4): [
                (1, -2, 1),
                (0, -1, 1),
                (2, -2, 0),
                (1, -1, 0),
                (0, 0, 0),
                (2, -1, -1),
                (1, 0, -1),
            ],
            (4, 1, 4): [
                (3, -3, 0),
                (2, -2, 0),
                (1, -1, 0),
                (0, 0, 0),
            ],
            (4, 1, 5): [(0, 0, 0), (0, 1, -1), (0, 2, -2), (0, 3, -3)],
            (3, 3, 5): [
                (0, 0, 0),
                (1, 0, -1),
                (0, 1, -1),
                (-1, 1, 0),
                (1, 1, -2),
                (0, 2, -2),
                (-1, 2, -1),
            ],
            (3, 5, 6): [
                (-2, 2, 0),
                (-2, 1, 1),
                (-2, 0, 2),
                (-1, -1, 2),
                (0, -2, 2),
                (0, -1, 1),
                (-1, 0, 1),
                (-1, 1, 0),
                (0, 0, 0),
            ],
            (4, 1, 6): [(0, 0, 0), (-1, 0, 1), (-2, 0, 2), (-3, 0, 3)],
        }

        for simulation_radius, sample_width, direction in tests:
            with self.subTest(
                simulation_radius=simulation_radius, sample_width=sample_width, direction=direction
            ):
                sample_needle = SampleNeedle(simulation_radius, sample_width, direction)

                found = sample_needle.select_sample_locations()
                expected = tests[(simulation_radius, sample_width, direction)]

                self.assertCountEqual(found, expected)

    def test_select_sample_locations_given_even_width_raises_value_error(self):
        simulation_radius = 3
        sample_width = 2
        direction = 1
        sample_needle = SampleNeedle(simulation_radius, sample_width, direction)

        with self.assertRaises(ValueError):
            sample_needle.select_sample_locations()

    def test_valid_coords_for_needle_direction_returns_correct_bool(self):
        tests = {(0, 0, 0, 1, 1): True, (-1, 0, 1, 6, 1): True, (10, 10, 2, 6, 1): False}
        for u, v, w, direction, half_width in tests:
            with self.subTest(u=u, v=v, w=w, direction=direction, half_width=half_width):
                found = SampleNeedle.valid_coords_for_needle_direction(
                    (u, v, w), direction, half_width
                )
                expected = tests[(u, v, w, direction, half_width)]
                self.assertEqual(found, expected)
