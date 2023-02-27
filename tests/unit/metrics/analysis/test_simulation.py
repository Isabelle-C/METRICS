import json

import unittest
from unittest.mock import mock_open
from unittest import mock

import pandas as pd
import numpy as np

from metrics.feature.continuous_feature import ContinuousFeature
from metrics.feature.discrete_feature import DiscreteFeature
from metrics.analysis.simulation import Simulation
from metrics.feature.feature import Feature


class TestSimulation(unittest.TestCase):
    @mock.patch("builtins.open", new_callable=mock_open)
    @mock.patch("metrics.analysis.simulation.json")
    def test_init_sets_attributes_from_file_name(self, json_mock, open_mock):
        key = "TEST_FAKE_JSON"
        seed = 14
        extension = ".json"
        path = "/path/to/file"
        simulation_file = f"{path}/{key}_{seed:02}{extension}"

        simulation_contents = {"seed": seed, "timepoints": [], "config": {"size": {"radius": 34}}}
        json_mock.load.return_value = simulation_contents

        simulation = Simulation(simulation_file)

        self.assertEqual(simulation_file, simulation.file)
        self.assertEqual(path, simulation.path)
        self.assertEqual(extension, simulation.extension)
        self.assertEqual(key, simulation.key)

    @mock.patch("builtins.open", new_callable=mock_open)
    @mock.patch("metrics.analysis.simulation.json")
    def test_init_sets_attributes_from_file_name_with_suffix(self, json_mock, open_mock):
        key = "TEST_FAKE_JSON"
        seed = 14
        suffix = ".PARAM"
        extension = ".json"
        path = "/path/to/file"
        simulation_file = f"{path}/{key}_{seed:02}{suffix}{extension}"

        simulation_contents = {"seed": seed, "timepoints": [], "config": {"size": {"radius": 34}}}
        json_mock.load.return_value = simulation_contents

        simulation = Simulation(simulation_file)

        self.assertEqual(simulation_file, simulation.file)
        self.assertEqual(path, simulation.path)
        self.assertEqual(extension, simulation.extension)
        self.assertEqual(key, simulation.key)

    @mock.patch("builtins.open", new_callable=mock_open)
    @mock.patch("metrics.analysis.simulation.json")
    def test_init_sets_attributes_from_data(self, json_mock, open_mock):
        seed = 14
        timepoints = [0.0, 0.5, 1.0]
        max_radius = 34
        simulation_file = f"/path/to/file/SIMULATION_FILE_{seed:02}.json"
        simulation_contents = {
            "seed": seed,
            "timepoints": [{"time": timepoint} for timepoint in timepoints],
            "config": {"size": {"radius": max_radius}},
        }

        json_mock.load.return_value = simulation_contents
        simulation = Simulation(simulation_file)

        self.assertCountEqual(timepoints, simulation.timepoints)
        self.assertEqual(seed, simulation.seed)
        self.assertEqual(max_radius, simulation.max_radius)

    @mock.patch("builtins.open", new_callable=mock_open)
    @mock.patch("metrics.analysis.simulation.json")
    def test_load_simulation_loads_existing_file(self, json_mock, open_mock):
        simulation_file = "/path/to/file/SIMULATION_FILE_00.json"
        simulation_contents = {"seed": 0, "timepoints": [], "config": {"size": {"radius": 34}}}

        json_mock.load.return_value = simulation_contents
        loaded_simulation = Simulation(simulation_file).load_simulation()

        open_mock.assert_called_with(
            "/path/to/file/SIMULATION_FILE/SIMULATION_FILE_00.json", "r", encoding="utf-8"
        )
        json_mock.load.assert_called_with(open_mock())
        self.assertDictEqual(simulation_contents, loaded_simulation)

    @mock.patch("builtins.open", new_callable=mock_open)
    @mock.patch("metrics.analysis.simulation.json")
    def test_load_simulation_loads_existing_file_with_suffix(self, json_mock, open_mock):
        simulation_file = "/path/to/file/SIMULATION_FILE_00.json"
        param_file = "/path/to/file/SIMULATION_FILE_00.PARAM.json"
        simulation_contents = {"seed": 0, "timepoints": [], "config": {"size": {"radius": 34}}}

        json_mock.load.return_value = simulation_contents
        loaded_simulation = Simulation(simulation_file).load_simulation(suffix=".PARAM")

        open_mock.assert_called_with(
            "/path/to/file/SIMULATION_FILE.PARAM/SIMULATION_FILE_00.PARAM.json",
            "r",
            encoding="utf-8",
        )
        json_mock.load.assert_called_with(open_mock())
        self.assertDictEqual(simulation_contents, loaded_simulation)

    def test_get_szudzik_pair_returns_correct_pairing_number(self):
        tests = [
            (0, 0, 0),
            (1, 1, 4),
            (2, 1, 11),
            (2, 3, 20),
            (3, 2, 23),
            (-5, 4, 49),
            (5, -4, 58.5),
            (-6, -3, 68.5),
        ]
        for u_given, v_given, expected in tests:
            with self.subTest(u_given=u_given, v_given=v_given):
                found = Simulation.get_szudzik_pair(u_given, v_given)
                self.assertEqual(found, expected)

    @mock.patch("builtins.open")
    def test_parse_timepoint_given_one_location_one_cell_returns_dataframe(self, open_mock):
        seed = 0
        max_radius = 34
        time = 0.0
        key = "SIMULATION_FILE"
        cell_location = [3, 0, -3, 0]
        max_height = 8.7
        meta_pref = 0.4
        migra_threshold = 3.0
        param_values = [None] * 10
        param_values[3] = max_height
        param_values[8] = meta_pref
        param_values[9] = migra_threshold

        file_key = f"/path/to/file/SIMULATION_FILE_{seed:02}"
        simulation_file = f"{file_key}.json"
        simulation_param_file = f"{file_key}.PARAM.json"

        simulation_contents = {
            "seed": seed,
            "config": {"size": {"radius": max_radius}},
            "timepoints": [
                {
                    "time": time,
                    "cells": [[cell_location, [[0, 4, 6, 0, 2250, []]]]],
                }
            ],
        }

        simulation_param_contents = {
            "seed": seed,
            "config": {"size": {"radius": max_radius}},
            "timepoints": [
                {
                    "time": time,
                    "cells": [[cell_location, [[0, 4, 6, 0, param_values]]]],
                }
            ],
        }

        mock_contents = {
            "/path/to/file/SIMULATION_FILE/SIMULATION_FILE_00.json": json.dumps(
                simulation_contents
            ),
            "/path/to/file/SIMULATION_FILE.PARAM/SIMULATION_FILE_00.PARAM.json": json.dumps(
                simulation_param_contents
            ),
        }
        open_mock.side_effect = lambda fname, *args, **kwargs: mock_open(
            read_data=mock_contents[fname]
        ).return_value

        expected_dict = {
            "key": [key],
            "seed": [seed],
            "time": [time],
            "coordinate": [Simulation.get_szudzik_pair(cell_location[0], cell_location[1])],
            "u": cell_location[0],
            "v": cell_location[1],
            "w": cell_location[2],
            "z": cell_location[3],
            "p": [0],
            "population": ["4"],
            "state": ["6"],
            "volume": [2250],
            "cycle": [float("nan")],
            "max_height": [max_height],
            "meta_pref": [meta_pref],
            "migra_threshold": [migra_threshold],
        }
        expected_df = pd.DataFrame(expected_dict)

        returned_df = Simulation(simulation_file).parse_timepoint(time)

        self.assertTrue(expected_df.equals(returned_df))

    @mock.patch("builtins.open")
    def test_parse_timepoint_given_two_location_two_cells_returns_dataframe(self, open_mock):
        seed = 0
        max_radius = 34
        time = 0.5
        key = "SIMULATION_FILE"
        cell_locations = [[5, 1, -6, 1], [6, 1, -7, 1]]
        max_heights = [8.7, 5.2]
        meta_prefs = [0.3, 0.35]
        migra_thresholds = [3.0, 4.0]
        cell_0_param_values = [None] * 10
        cell_0_param_values[3] = max_heights[0]
        cell_0_param_values[8] = meta_prefs[0]
        cell_0_param_values[9] = migra_thresholds[0]
        cell_1_param_values = [None] * 10
        cell_1_param_values[3] = max_heights[1]
        cell_1_param_values[8] = meta_prefs[1]
        cell_1_param_values[9] = migra_thresholds[1]

        file_key = f"/path/to/file/SIMULATION_FILE_{seed:02}"
        simulation_file = f"{file_key}.json"
        simulation_param_file = f"{file_key}.PARAM.json"

        simulation_contents = {
            "seed": seed,
            "config": {"size": {"radius": max_radius}},
            "timepoints": [
                {
                    "time": time,
                    "cells": [
                        [cell_locations[0], [[1, 0, 0, 1, 3200, [1440, 1350]]]],
                        [cell_locations[1], [[1, 3, 1, 2, 3000, [1300, 1460]]]],
                    ],
                }
            ],
        }

        simulation_param_contents = {
            "seed": seed,
            "config": {"size": {"radius": max_radius}},
            "timepoints": [
                {
                    "time": time,
                    "cells": [
                        [cell_locations[0], [[1, 0, 0, 1, cell_0_param_values]]],
                        [cell_locations[1], [[1, 3, 1, 2, cell_1_param_values]]],
                    ],
                }
            ],
        }

        mock_contents = {
            "/path/to/file/SIMULATION_FILE/SIMULATION_FILE_00.json": json.dumps(
                simulation_contents
            ),
            "/path/to/file/SIMULATION_FILE.PARAM/SIMULATION_FILE_00.PARAM.json": json.dumps(
                simulation_param_contents
            ),
        }
        open_mock.side_effect = lambda fname, *args, **kwargs: mock_open(
            read_data=mock_contents[fname]
        ).return_value

        expected_dict = {
            "key": [key] * 2,
            "seed": [seed] * 2,
            "time": [time] * 2,
            "coordinate": [
                Simulation.get_szudzik_pair(cell_location[0], cell_location[1])
                for cell_location in cell_locations
            ],
            "u": [cell_location[0] for cell_location in cell_locations],
            "v": [cell_location[1] for cell_location in cell_locations],
            "w": [cell_location[2] for cell_location in cell_locations],
            "z": [cell_location[3] for cell_location in cell_locations],
            "p": [1, 2],
            "population": ["0", "3"],
            "state": ["0", "1"],
            "volume": [3200, 3000],
            "cycle": [np.round(np.mean([1440, 1350])), np.round(np.mean([1300, 1460]))],
            "max_height": max_heights,
            "meta_pref": meta_prefs,
            "migra_threshold": migra_thresholds,
        }
        expected_df = pd.DataFrame(expected_dict)

        returned_df = Simulation(simulation_file).parse_timepoint(timepoint=time)

        self.assertTrue(expected_df.equals(returned_df))

    @mock.patch("builtins.open", new_callable=mock_open)
    def test_parse_timepoint_given_one_location_two_cells_returns_dataframe(self, open_mock):
        seed = 0
        max_radius = 34
        time = 1.0
        key = "SIMULATION_FILE"
        max_heights = [8.8, 5.2]
        meta_prefs = [0.36, 0.37]
        migra_thresholds = [2.8, 3.2]
        cell_0_param_values = [None] * 10
        cell_0_param_values[3] = max_heights[0]
        cell_0_param_values[8] = meta_prefs[0]
        cell_0_param_values[9] = migra_thresholds[0]
        cell_1_param_values = [None] * 10
        cell_1_param_values[3] = max_heights[1]
        cell_1_param_values[8] = meta_prefs[1]
        cell_1_param_values[9] = migra_thresholds[1]

        file_key = f"/path/to/file/SIMULATION_FILE_{seed:02}"
        simulation_file = f"{file_key}.json"
        simulation_param_file = f"{file_key}.PARAM.json"

        simulation_contents = {
            "seed": seed,
            "config": {"size": {"radius": max_radius}},
            "timepoints": [
                {
                    "time": time,
                    "cells": [
                        [
                            [-3, 2, -1, 2],
                            [[0, 1, 3, 4, 3001, [1320, 1440]], [4, 0, 1, 0, 2500, [1440]]],
                        ]
                    ],
                }
            ],
        }

        simulation_param_contents = {
            "seed": seed,
            "config": {"size": {"radius": max_radius}},
            "timepoints": [
                {
                    "time": time,
                    "cells": [
                        [
                            [-3, 2, -1, 2],
                            [
                                [0, 1, 3, 4, cell_0_param_values],
                                [4, 0, 1, 0, cell_1_param_values],
                            ],
                        ]
                    ],
                }
            ],
        }

        mock_contents = {
            "/path/to/file/SIMULATION_FILE/SIMULATION_FILE_00.json": json.dumps(
                simulation_contents
            ),
            "/path/to/file/SIMULATION_FILE.PARAM/SIMULATION_FILE_00.PARAM.json": json.dumps(
                simulation_param_contents
            ),
        }

        open_mock.side_effect = lambda fname, *args, **kwargs: mock_open(
            read_data=mock_contents[fname]
        ).return_value

        expected_dict = {
            "key": [key] * 2,
            "seed": [seed] * 2,
            "time": [time] * 2,
            "coordinate": [Simulation.get_szudzik_pair(-3, 2)] * 2,
            "u": [-3, -3],
            "v": [2, 2],
            "w": [-1, -1],
            "z": [2, 2],
            "p": [4, 0],
            "population": ["1", "0"],
            "state": ["3", "1"],
            "volume": [3001, 2500],
            "cycle": [np.round(np.mean([1320, 1440])), np.round(np.mean([1440]))],
            "max_height": max_heights,
            "meta_pref": meta_prefs,
            "migra_threshold": migra_thresholds,
        }
        expected_df = pd.DataFrame(expected_dict)

        returned_df = Simulation(simulation_file).parse_timepoint(timepoint=time)

        self.assertTrue(expected_df.equals(returned_df))

    @mock.patch("builtins.open", new_callable=mock_open)
    @mock.patch("metrics.analysis.simulation.json")
    def test_parse_timepoint_given_nonexistent_timepoint_raises_value_error(
        self, json_mock, open_mock
    ):
        seed = 0
        time = 1.0
        key = "SIMULATION_FILE"
        simulation_contents = {
            "seed": seed,
            "config": {"size": {"radius": 34}},
            "timepoints": [{"time": time, "cells": [[]]}],
        }
        json_mock.load.return_value = simulation_contents

        with self.assertRaises(ValueError):
            Simulation(f"/path/to/file/{key}_{seed:02}.json").parse_timepoint(timepoint=0.0)

    def test_get_feature_object_given_nonexistent_feature_raises_value_error(self):
        with self.assertRaises(ValueError):
            Simulation.get_feature_object("nonexistent_feature")

    def test_get_feature_object_given_invalid_feature_raises_value_error(self):
        with self.assertRaises(ValueError):
            Simulation.get_feature_object("key")

    def test_get_feature_object_given_continuous_feature_returns_feature(self):
        expected_feature = ContinuousFeature("volume", "REAL", False)
        found_feature = Simulation.get_feature_object("volume")
        self.assertEqual(expected_feature.name, found_feature.name)

    def test_get_feature_object_given_discrete_feature_returns_feature(self):
        expected_feature = DiscreteFeature("population", "TEXT", False)
        found_feature = Simulation.get_feature_object("population")
        self.assertEqual(expected_feature.name, found_feature.name)
