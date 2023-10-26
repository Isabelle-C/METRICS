from typing import List, Optional

import numpy as np
import pandas as pd

from metrics.analysis.database import Database


class Script:
    """
    Script for visualizing the data.
    """

    @staticmethod
    def create_databases(
        population: str,
        context: str,
        heterogeneity_levels: list = ["00", "10", "20", "30", "40", "50"],
    ) -> List[Database]:
        """
        Creates database files for each context.

        Parameters
        ----------
        population : str
            The population.
        context : str
            The context.
        heterogeneity_levels : list
            The heterogeneity levels.

        Returns
        -------
        : List[Database]
            List of database objects.
        """
        database_list = []

        for heterogeneity in heterogeneity_levels:
            database_list.append(
                Database(f"./data/databases/{population}_{context}_{heterogeneity}.db")
            )

        return database_list

    @staticmethod
    def select_data(
        database_list: List[Database],
        context: str,
        reference_time: Optional[str] = None,
        observation_time: Optional[str] = None,
        feature: Optional[str] = None,
        comparison: Optional[dict] = None,
    ) -> pd.DataFrame:
        """
        Selects data from the database.

        Parameters
        ----------
        database_list : List[Database]
            The database object.
        reference_time : Optional[str]
            The reference time.
        observation_time : Optional[str]
            The observation time.
        feature : Optional[str]
            The feature.
        comparison: Optional[dict]
            The comparison group.

        Returns
        -------
        combined_table : pd.DataFrame
            Combined selected dataframe.
        """
        query_list: List[str] = []
        if reference_time is not None:
            query_list.append(f"reference_time = {reference_time}")
        if observation_time is not None:
            query_list.append(f"obervation_time = {observation_time}")
        if feature is not None:
            query_list.append(f"feature = '{feature}'")
        if comparison is not None:
            query_list.append(f"comparison_group = '{' | '.join(comparison.values())}'")

        combined_table: list = []
        for database in database_list:
            data = database.execute_query(f"SELECT * FROM stats WHERE {' AND '.join(query_list)}")

            # Add context column and change key column
            data["context"] = context

            key_split = data["key"].str.split("_", expand=True)
            selected_columns = key_split[[4, 3]]
            selected_columns.columns = ["heterogeneity", "cell_line"]

            data = pd.concat([data, selected_columns], axis=1)
            data = data.drop("key", axis=1)

            data["heterogeneity"] = data["heterogeneity"].astype(int)
            data["divergence"] = data["divergence"].replace("NULL", np.nan).astype(float)

            combined_table.append(data)

        return pd.concat(combined_table, axis=0)

    @staticmethod
    def find_unique_variables(
        data: pd.DataFrame, variable: Optional[str], column_name: Optional[str] = "category"
    ) -> np.ndarray:
        """
        Find unique variables.

        Parameters
        ----------
        data : pd.DataFrame
            The data.
        variable : Optional[str]
            The variable.
        column_name : Optional[str]
            The column name.

        Returns
        -------
        unique_variables : np.ndarray
            Unique variables.
        """
        unique_variables = data[column_name].unique()

        if variable == "population":
            # Create a mask to identify the items to keep
            mask = unique_variables != "4"

            # Remove item from the array
            unique_variables = unique_variables[mask]
        return unique_variables
