"""
Base classes for the core data models
"""


class DataSource:
    """
    core functionality for all data sources
    """
    # Metadata required by all Data sources
    name = None
    data_type = None
    bounding_box = None
    bounds = None
    info_text = None

    @classmethod
    def get_metadata(self):
        """
        returns a dict of the metadata for this data source
        """
        metadata = {'name': self.name,
                    'data_type': self.data_type,
                    'bounding_box': self.bounding_box,
                    'bounds': self.bounds,
                    'info_text': self.info_text
                    }
        return metadata


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
