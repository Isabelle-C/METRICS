import unittest

from metrics.analysis.coordinate import Coordinate


class TestCoordinate(unittest.TestCase):
    def test_coordinate_makes_coordinate(self):
        coordinate = Coordinate((1, 0, -1))
        self.assertEqual(coordinate.u, 1)
        self.assertEqual(coordinate.v, 0)
        self.assertEqual(coordinate.w, -1)

    def test_coordinate_raise_value_error(self):
        with self.assertRaises(ValueError):
            Coordinate((1, 1, 1))
