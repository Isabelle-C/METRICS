import sqlite3
import pandas as pd


class Database:
    """
    TODO: add docstring
    """

    def __init__(self, database_file):
        """
        TODO: add docstring
        """
        self.file = database_file

    def __str__(self):
        attributes = [("file", self.file)]

        attribute_strings = [f"{key:10} = {value}" for key, value in attributes]
        string = "\n\t".join(attribute_strings)
        return "DATABASE\n\t" + string

    def get_connection(self):
        """
        TODO: add docstring
        """
        # TODO: connect to database and return connection
        return None

    def create_table(self, table, simulation):
        """
        TODO: add docstring
        """
        # TODO: connect to table, create table, and close connection (what
        # method is useful here?)

    def add_dataframe(self, table, dataframe):
        """
        TODO: add docstring
        """
        # TODO: connect to table, check if table exists (create if not), add
        # dataframe to the table (check if data already exists!), and close
        # connection

    def load_dataframe(self, table, key):
        """
        TODO: add docstring
        """
        # TODO: connect to table, get data for the specific simulation key as a
        # dataframe, and close connection (what method is useful here?)
        return pd.DataFrame()

    @staticmethod
    def make_create_table_query(table):
        """
        TODO: add docstring
        """
        # TODO: return query string that creates table (if it doesn't exist)
        # from the feature list of the given table type (what methods from
        # Feature are useful here?)
        return ""

    @staticmethod
    def make_select_from_query(table, key):
        """
        TODO: add docstring
        """
        # TODO: return query string that selects items matching the key from
        # the given table
        return ""
