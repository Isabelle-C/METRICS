class Feature:
    """
    Representation of a data feature.

    Attributes
    ----------
    name :
        The name of the feature.
    affinity : {"NUMERIC", "INTEGER", "REAL", "TEXT", "BLOB"}
        The SQLite3 type affinity of the feature.
    is_null :
        True if feature data can be null, False otherwise.
    """

    def __init__(self, name: str, affinity: str, is_null: bool):
        valid_dtypes = ["NUMERIC", "INTEGER", "REAL", "TEXT", "BLOB"]
        if affinity.upper() not in valid_dtypes:
            raise TypeError(f"Data type must be one of {valid_dtypes}")

        self.name = name
        self.affinity = affinity
        self.is_null = is_null

    def __str__(self) -> str:
        attributes = [
            ("name", self.name),
            ("affinity", self.affinity),
            ("is_null", self.is_null),
        ]

        attribute_strings = [f"{key} = {value}" for key, value in attributes]
        string = " | ".join(attribute_strings)
        return f"FEATURE [{string}]"

    def make_query(self) -> str:
        """
        Make SQLite3 CREATE TABLE query column definition.

        Column definition is ``(name AFFINITY)`` if the feature can be null.
        Column definition is ``(name AFFINITY NOT NULL)`` if the feature can not be null.

        Returns
        -------
        :
            SQLite3 column definition.
        """
        if self.is_null:
            whether_null = ""
        else:
            whether_null = "NOT NULL"
        return f"{self.name} {self.affinity} {whether_null}"
