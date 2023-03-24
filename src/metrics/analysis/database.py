from typing import Union

import sqlite3
import pandas as pd

from metrics.analysis.simulation import Simulation
from metrics.analysis.analysis import Analysis


class Database:
    """
    Wrapper for interacting with SQLite3 database.

    Attributes
    ----------
    file :
        Database file name.
    """

    def __init__(self, database_file: str):
        if database_file == ":memory:":
            raise AttributeError("Cannot use in-memory database.")

        if ".db" not in database_file:
            raise AttributeError("Input should be a database file with .db extension.")

        if " " in database_file:
            raise AttributeError("Cannot have space in database name.")

        self.file = database_file

    def __str__(self) -> str:
        attributes = [("file", self.file)]

        attribute_strings = [f"{key:10} = {value}" for key, value in attributes]
        string = "\n\t".join(attribute_strings)
        return "DATABASE\n\t" + string

    def get_connection(self) -> sqlite3.Connection:
        """
        Obtains connection to a SQLite database.

        Returns
        -------
        :
            Connection to the database file.
        """
        connection = sqlite3.connect(self.file, uri=True)
        return connection

    def create_table(self, table_name: str, table_spec: Union[Simulation, Analysis]) -> None:
        """
        Creates table in connected database.

        Parameters
        ----------
        table_name :
            The name of the table.
        table_spec :
            Object specifying the table columns (Simulation or Analysis object).
        """
        connection = self.get_connection()
        cursor = connection.cursor()
        query = Database.make_create_table_query(table_name, table_spec)

        cursor.execute(query)
        connection.commit()
        connection.close()

    def add_dataframe(self, table_name: str, dataframe: pd.DataFrame) -> None:
        """
        Adds data into specified table.

        If table exists, then data is appended to the existing table.

        Parameters
        ----------
        table_name :
            The name of the table.
        dataframe :
            Data to add to table.
        """
        connection = self.get_connection()

        dataframe.to_sql(name=table_name, con=connection, if_exists="append", index=False)

        connection.commit()
        connection.close()

    def load_dataframe(self, table_name: str, key: str) -> pd.DataFrame:
        """
        Load data for specified simulation key.

        Parameters
        ----------
        table_name :
            The name of the table.
        key :
            Simulation key.

        Returns
        -------
        :
            Selected data from the SQLite table.
        """
        connection = self.get_connection()
        query = self.make_select_from_query(table_name, key)
        data = pd.read_sql_query(sql=query, con=connection)

        connection.commit()
        connection.close()
        return data

    def delete_data_from_table(self, table_name: str) -> None:
        """
        Delete data in specified table if it exists.

        Parameters
        ----------
        table_name :
            Name of the table.
        """
        connection = self.get_connection()
        cursor = connection.cursor()
        query = f"DELETE FROM {table_name} WHERE 1=1;"

        cursor.execute(query)

        connection.commit()
        connection.close()

    def drop_table(self, table_name: str) -> None:
        """
        Drop table.

        Parameters
        ----------
        table_name :
            Name of the table.
        """
        connection = self.get_connection()
        cursor = connection.cursor()

        query = f"DROP TABLE IF EXISTS {table_name};"
        cursor.execute(query)

        connection.commit()
        connection.close()

    @staticmethod
    def make_create_table_query(table_name: str, table_spec: Union[Simulation, Analysis]) -> str:
        """
        Return query string that creates the SQLite table.

        Parameters
        ----------
        table_name :
            The name of the table.
        table_spec :
            Object specifying the table columns (Simulation or Analysis object).

        Returns
        -------
        :
            Query string for creating table.
        """
        feature_list = table_spec.get_feature_list()

        table_columns = []
        for feature in feature_list:
            table_columns.append(feature.make_query())

        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({','.join(table_columns)});"
        return query

    @staticmethod
    def make_select_from_query(table_name: str, key: str) -> str:
        """
        Return query string that selects rows with the specified key.

        Parameters
        ----------
        table_name :
            The name of the table.
        key :
            Simulation key.

        Returns
        -------
        :
            Query string for selecting from database table.
        """
        query = f"SELECT * FROM {table_name} WHERE key= '{key}';"
        return query
