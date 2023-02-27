import unittest
from unittest import mock

import pandas as pd
import sqlite3

from metrics.analysis.database import Database
from metrics.feature.feature import Feature


class TestDatabase(unittest.TestCase):
    def test_init_sets_attribute(self):
        database_name = "test.db"
        database = Database(database_name)
        self.assertEqual(database_name, database.file)

    def test_init_in_memory_raises_attributeerror(self):
        with self.assertRaises(AttributeError):
            Database(":memory:")

    def test_init_filename_withspaces_raises_attributeerror(self):
        with self.assertRaises(AttributeError):
            Database("x x x.db")

    def test_init_filename_without_db_raises_attributeerror(self):
        with self.assertRaises(AttributeError):
            Database("x")
            Database("")

    @mock.patch("metrics.analysis.database.sqlite3")
    def test_get_connection_returns_connection(self, sqlite3_mock):
        connection_object = mock.Mock(spec=sqlite3.Connection)
        sqlite3_mock.connect.return_value = connection_object

        database_name = "test.db"
        database = Database(database_name)
        connection = database.get_connection()

        # check if mock object calls correct parameter
        sqlite3_mock.connect.assert_called_with(database_name, uri=True)
        self.assertIsInstance(connection, sqlite3.Connection)

    @mock.patch("metrics.analysis.database.sqlite3")
    def test_create_table_creates_table(self, sqlite3_mock):
        connection_object = mock.Mock(spec=sqlite3.Connection)
        sqlite3_mock.connect.return_value = connection_object
        cursor_object = mock.Mock(spec=sqlite3.Cursor)
        connection_object.cursor.return_value = cursor_object

        table_name = "fake_table"
        feature_string = "test_string"

        feature = mock.Mock(spec=Feature)
        feature.make_query.return_value = feature_string

        object = mock.Mock()
        object.get_feature_list.return_value = [feature]

        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({feature_string});"

        Database("test.db").create_table(table_name, object, stats=True, info=False)
        cursor_object.execute.assert_called_with(query)
        connection_object.commit.assert_called()
        connection_object.close.assert_called()

    @mock.patch("metrics.analysis.database.sqlite3")
    def test_add_dataframe_adds_data_to_table(self, sqlite3_mock):
        connection_object = mock.Mock(spec=sqlite3.Connection)
        sqlite3_mock.connect.return_value = connection_object

        table_name = "table_name"
        dataframe = mock.Mock(spec=pd.DataFrame)

        Database("test.db").add_dataframe(table_name, dataframe)
        dataframe.to_sql.assert_called_with(
            name=table_name,
            con=connection_object,
            if_exists="append",
            index=False,
        )

        connection_object.commit.assert_called()
        connection_object.close.assert_called()

    @mock.patch("metrics.analysis.database.pd")
    @mock.patch("metrics.analysis.database.sqlite3")
    def test_load_dataframe_returns_data(self, sqlite3_mock, pd_mock):
        connection_object = mock.Mock(spec=sqlite3.Connection)
        sqlite3_mock.connect.return_value = connection_object

        dataframe = mock.Mock(spec=pd.DataFrame)
        pd_mock.read_sql_query.return_value = dataframe

        table_name = "fake_table"
        select_key = "y"
        input_query = f"SELECT * FROM {table_name} WHERE key= '{select_key}';"
        data = Database("test.db").load_dataframe(table_name, select_key)

        self.assertEqual(dataframe, data)
        pd_mock.read_sql_query.assert_called_with(sql=input_query, con=connection_object)
        connection_object.commit.assert_called()
        connection_object.close.assert_called()

    def test_make_create_table_query_creates_query(self):
        table_name = "fake_table"
        feature_string = "seed integer NOT NULL"
        feature_string2 = "x y z"

        feature = mock.Mock(spec=Feature)
        feature.make_query.return_value = feature_string
        feature2 = mock.Mock(spec=Feature)
        feature2.make_query.return_value = feature_string2

        fake_object = mock.Mock()
        fake_object.get_feature_list.return_value = [
            feature,
            feature2,
        ]

        expected = f"CREATE TABLE IF NOT EXISTS {table_name} ({feature_string},{feature_string2});"
        found = Database.make_create_table_query(table_name, fake_object, stats=True, info=False)
        self.assertEqual(expected, found)

    def test_make_select_from_query_returns_query(self):
        table_name = "fake_table"
        fake_key = "y"
        expected = f"SELECT * FROM {table_name} WHERE key= '{fake_key}';"
        found = Database.make_select_from_query(table_name, fake_key)
        self.assertEqual(expected, found)


if __name__ == "__main__":
    unittest.main()
