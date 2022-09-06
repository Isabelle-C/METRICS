import unittest

import pandas as pd
import numpy as np

from abmbiopsy.sample import Sample
from abmbiopsy.simulation import Simulation


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

    def test_sample_data_extracts_sample_given_data(self):
        coordinates = [(-3, 2, -1), (-5, 4, -1), (-6, 4, -2)]

        data_dict = {
            "key": ["SIMULATION_FILE_A", "SIMULATION_FILE_B", "SIMULATION_FILE_C"],
            "seed": [0, 1, 2],
            "time": [1.0, 1.0, 1.0],
            "coordinate": [
                Simulation.get_szudzik_pair(-3, 2),
                Simulation.get_szudzik_pair(-5, 4),
                Simulation.get_szudzik_pair(-6, 4),
            ],
            "u": [-3, -5, -6],
            "v": [2, 4, 4],
            "w": [-1, -1, -2],
        }
        data = pd.DataFrame(data_dict)

        selected_coordinates = [coordinates[0], coordinates[2]]

        expected_dict = {
            "key": [data_dict["key"][0], data_dict["key"][2]],
            "seed": [data_dict["seed"][0], data_dict["seed"][2]],
            "time": [data_dict["time"][0], data_dict["time"][2]],
            "coordinate": [data_dict["coordinate"][0], data_dict["coordinate"][2]],
            "u": [data_dict["u"][0], data_dict["u"][2]],
            "v": [data_dict["v"][0], data_dict["v"][2]],
            "w": [data_dict["w"][0], data_dict["w"][2]],
        }
        expected_df = pd.DataFrame(expected_dict)

        sample = Sample("needle", 1)
        returned_df = sample.sample_data(selected_coordinates, data)

        self.assertTrue(expected_df.equals(returned_df))
