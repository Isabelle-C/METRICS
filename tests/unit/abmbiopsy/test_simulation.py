import unittest
from unittest.mock import mock_open
from unittest import mock

from abmbiopsy.feature import Feature
from abmbiopsy.simulation import Simulation


class TestSimulation(unittest.TestCase):
    @mock.patch("builtins.open", new_callable=mock_open)
    @mock.patch("abmbiopsy.simulation.json")
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
    @mock.patch("abmbiopsy.simulation.json")
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
    @mock.patch("abmbiopsy.simulation.json")
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
    @mock.patch("abmbiopsy.simulation.json")
    def test_load_simulation_loads_existing_file(self, json_mock, open_mock):
        simulation_file = "/path/to/file/SIMULATION_FILE_00.json"
        simulation_contents = {"seed": 0, "timepoints": [], "config": {"size": {"radius": 34}}}

        json_mock.load.return_value = simulation_contents
        loaded_simulation = Simulation(simulation_file).load_simulation()

        open_mock.assert_called_with(simulation_file, "r")
        json_mock.load.assert_called_with(open_mock())
        self.assertDictEqual(simulation_contents, loaded_simulation)

    @mock.patch("builtins.open", new_callable=mock_open)
    @mock.patch("abmbiopsy.simulation.json")
    def test_load_simulation_loads_existing_file_with_suffix(self, json_mock, open_mock):
        simulation_file = "/path/to/file/SIMULATION_FILE_00.json"
        param_file = "/path/to/file/SIMULATION_FILE_00.PARAM.json"
        simulation_contents = {"seed": 0, "timepoints": [], "config": {"size": {"radius": 34}}}

        json_mock.load.return_value = simulation_contents
        loaded_simulation = Simulation(simulation_file).load_simulation(suffix=".PARAM")

        open_mock.assert_called_with(param_file, "r")
        json_mock.load.assert_called_with(open_mock())
        self.assertDictEqual(simulation_contents, loaded_simulation)

    def test_get_feature_list_returns_list(self):
        output = Simulation.get_feature_list()
        self.assertIsInstance(output, list)

    def test_get_feature_list_returns_list_of_feature_objects(self):
        output = Simulation.get_feature_list()
        for i in output:
            self.assertIsInstance(i, Feature)
