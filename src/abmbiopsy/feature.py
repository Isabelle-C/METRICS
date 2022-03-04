class Feature:
    """
    Representation of a data feature.
    TODO: update docstring with attributes
    """

    def __init__(self, name, dtype, is_null):
        """
        Initialize Feature with name.

        Parameters
        ----------
        name : str
            The name of the feature.

        TODO: update docstring
        """
        self.name = name
        self.dtype = dtype
        self.is_null = is_null

    def __str__(self):
        attributes = [
            ("name", self.name),
            ("dtype", self.dtype),
            ("is_null", self.is_null),
        ]

        attribute_strings = [f"{key} = {value}" for key, value in attributes]
        string = " | ".join(attribute_strings)
        return f"FEATURE [{string}]"

    def make_query(self):
        """
        TODO: add docstring
        """
        # Create query that defines the SQL column for the feature:
        #    name dtype NOT NULL (if is_null is False) OR
        #    name dtype NULL (if is_null is True)
        return ""
