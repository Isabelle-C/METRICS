class Sample:
    """
    Representation of a simulated sample.

    Sampling is intended to represent a clinical biopsy of a tumor. The
    punch samples represent punch biopsies, which use a circular blade to
    remove a tissue sample. The needle samples represent fine-needle
    aspiration biopsies, which use a hollow needle to remove a tissue
    sample.

    Attributes
    ----------
    shape : {'punch', 'needle'}
        Shape of the sample.
    radius : int
        Radius at which sample is taken.
    """

    def __init__(self, sample_shape, sample_radius):
        """
        TODO: add docstring
        """
        self.shape = sample_shape
        self.radius = sample_radius

    def __str__(self):
        attributes = [
            ("shape", self.shape),
            ("radius", self.radius),
        ]

        attribute_strings = [f"{key} = {value}" for key, value in attributes]
        string = " | ".join(attribute_strings)
        return f"SAMPLE [{string}]"

    def sample_data(self, data):
        """
        Extract sample from given data.
        TODO: update docstring
        """
        # TODO: make list of coordinates for the given sample

        # TODO: filter the dataframe for coordinates that match the list of
        # sample coordinates

        return data
