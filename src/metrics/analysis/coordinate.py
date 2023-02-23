class Coordinate:
    """
    Representation of a coordinate.

    Attributes
    ----------
    u : int
        U coordinate.
    v : int
        V coordinate.
    w : int
        W coordinate.
    key : str
        Coordinate key.
    """

    def __init__(self, coordinate: tuple):

        if sum(coordinate) != 0:
            raise ValueError("Coordinate is invalid.")
        self.u = coordinate[0]
        self.v = coordinate[1]
        self.w = coordinate[2]
        self.key = f"{coordinate}"
