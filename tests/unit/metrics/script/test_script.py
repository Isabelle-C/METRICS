import unittest
from unittest.mock import patch, MagicMock

import pandas as pd
import numpy as np

pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)

from metrics.analysis.analysis import Analysis
from metrics.analysis.database import Database
from metrics.analysis.simulation import Simulation
from metrics.analysis.experiment import Experiment
from metrics.feature.continuous_feature import ContinuousFeature
from metrics.script.script import Script


class ScriptTests(unittest.TestCase):
    def setUp(self):
        simulation_key = "POPULATION_HETEROGENEITY_C_A_10"
        # Create a temporary DataFrame for testing
        self.data = pd.DataFrame(
            {
                "comparison_group": [
                    "simulation | punch_10",
                    "simulation | punch_10",
                    "simulation | punch_5",
                    "simulation | punch_5",
                    "simulation | punch_10",
                    "simulation | punch_10",
                ],
                "key": [simulation_key] * 6,
                "seed": [0] * 6,
                "reference_time": [8.0] * 4 + [10.0] * 2,
                "obervation_time": [8.0] * 4 + [8.0] * 2,
                "reference_key": ["simulation"] * 6,
                "obervation_key": ["punch-R10-(0, 0, 0)"] * 2
                + ["punch-R5-(0, 0, 0)"] * 2
                + ["punch-R10-(0, 0, 0)"] * 2,
                "feature": ["feature_name"] * 6,
                "category": ["NULL"] * 6,
                "pvalue": [1.0, 1.0, 40.0, 20.0, 5.0, 5.0],
                "divergence": [2.0, 2.0, 40.0, 20.0, 8.0, 8.0],
            }
        )

    @patch("metrics.script.script.Database")
    def test_create_databases(self, db_mock):
        def side_effect(file_in):
            return MagicMock(file=file_in)

        # Configure the mock to use the side effect function
        db_mock.side_effect = side_effect

        population = "test"
        context = "test_context"
        databases = Script.create_databases(population, context)

        # Check if the expected number of databases is created
        self.assertEqual(len(databases), 6)

        # Check if the file paths are correct
        expected_paths = [
            f"./data/databases/{population}_{context}_00.db",
            f"./data/databases/{population}_{context}_10.db",
            f"./data/databases/{population}_{context}_20.db",
            f"./data/databases/{population}_{context}_30.db",
            f"./data/databases/{population}_{context}_40.db",
            f"./data/databases/{population}_{context}_50.db",
        ]
        for i, db in enumerate(databases):
            self.assertEqual(db.file, expected_paths[i])

    @patch("metrics.script.script.Database")
    def test_select_data(self, db_mock):
        # Insert test data into the database
        comparison = {"reference": "simulation", "observation": "punch_10"}

        db_mock.execute_query.return_value = pd.DataFrame(
            {
                "comparison_group": [
                    "simulation | punch_10",
                    "simulation | punch_10",
                ],
                "key": ["POPULATION_HETEROGENEITY_C_A_10"] * 2,
                "seed": [0] * 2,
                "reference_time": [8.0] * 2,
                "obervation_time": [8.0] * 2,
                "reference_key": ["simulation"] * 2,
                "obervation_key": ["punch-R10-(0, 0, 0)"] * 2,
                "feature": ["feature_name"] * 2,
                "category": ["NULL"] * 2,
                "pvalue": [1.0, 1.0],
                "divergence": [2.0, 2.0],
            }
        )

        # Call the select_data method
        database_list = [db_mock]
        context = "test_context"
        selected_data = Script.select_data(
            database_list,
            context,
            reference_time=8.0,
            observation_time=8.0,
            feature="feature_name",
            comparison=comparison,
        )

        # Check if the returned data is a DataFrame
        self.assertIsInstance(selected_data, pd.DataFrame)

        # Check if the data is correctly selected
        expected_data = pd.DataFrame(
            {
                "comparison_group": ["simulation | punch_10"] * 2,
                "seed": [0] * 2,
                "reference_time": [8.0] * 2,
                "obervation_time": [8.0] * 2,
                "reference_key": ["simulation"] * 2,
                "obervation_key": ["punch-R10-(0, 0, 0)"] * 2,
                "feature": ["feature_name"] * 2,
                "category": ["NULL"] * 2,
                "pvalue": [1.0, 1.0],
                "divergence": [2.0, 2.0],
                "context": ["test_context"] * 2,
                "heterogeneity": [10] * 2,
                "cell_line": ["A"] * 2,
            }
        )
        print(selected_data)
        pd.testing.assert_frame_equal(selected_data, expected_data)

    def test_find_unique_variables(self):
        data = pd.DataFrame({"category": ["A", "B", "C", "C"], "value": [1, 2, 3, 4]})
        variable = "population"
        unique_variables = Script.find_unique_variables(data, variable)

        # Check if the returned value is a numpy array
        self.assertIsInstance(unique_variables, np.ndarray)

        # Check if the unique variables are correctly identified
        expected_variables = np.array(["A", "B", "C"])
        np.testing.assert_array_equal(unique_variables, expected_variables)


if __name__ == "__main__":
    unittest.main()
