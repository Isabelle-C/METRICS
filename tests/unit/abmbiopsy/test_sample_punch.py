import unittest

from abmbiopsy.sample_punch import SamplePunch


class TestSamplePunch(unittest.TestCase):
    def test_select_sample_locations(self):
        tests = {
            1: [(0, 0, 0)],
            2: [
                (0, 0, 0),
                (0, 1, -1),
                (0, -1, 1),
                (1, 0, -1),
                (-1, 0, 1),
                (-1, 1, 0),
                (1, -1, 0),
            ],
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
                sample_punch = SamplePunch(sample_radius)
                found = sample_punch.select_sample_locations()

                expected = tests[sample_radius]

                self.assertCountEqual(found, expected)
