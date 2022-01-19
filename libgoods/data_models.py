"""
Base classes for the core data models
"""


class DataSource:
    """
    core functionality for all data sources
    """
    @property
    def bounds():
        """
        Property that returns the bounds of the model

        geo-json compatible polygon ?
        """

    @property
    def valid_times():
        """
        the start and end time of the data currently available
        """


class Shoreline(DataSource):
    """
    class for acccessing maps from shoreline
    """


class Currents(DataSource):
    """
    class that represents a gridded current
    """


class Winds(DataSource):
    """
    class that represents a gridded wind
    """
