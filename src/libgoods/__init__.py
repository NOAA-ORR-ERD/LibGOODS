"""

libgoods package

Package for working with various data sources of model results, etc.

Essentially anything needed by the NOAA GNOME system

Oceanographic currents

Surface Winds

Shorelines

etc...

Most of the core functionality you need as an end user is in the "api" module::

  from libgoods import api

"""

from dataclasses import dataclass
from pathlib import Path

__version__ = "2.2.3dev"

# some basic config:
# We could make this fancier for sure, but

class UnsetConfigError(AttributeError):
    """
    For when someone tries to access an unset config parameter.
    """

@dataclass
class Config:
    """
    Class for keeping track setting and accessing the configuration of libgoods
    """

    archive_dir: Path = None
    shoreline_dir: Path = None

    def __setattr__(self, prop, val):
        """
        magic to make sure the paths are all Path objects,
        even if someone sets it to a string
        """
        path_attrs = {"archive_dir", "shoreline_dir"}
        if val is not None:
            if prop in path_attrs:
                val = Path(val)
        super().__setattr__(prop, val)

    # def __getattribute__(self, attr):
    #     """
    #     magic to raise an exception if you try to use an unset config parameter
    #     """
    #     # Calling the super class to avoid recursion
    #     val = super().__getattribute__(attr)
    #     if val is None:
    #         raise UnsetConfigError(f"The config paramter: {attr} has not been set.\n"
    #                                f"use: `libgoods.config.{attr} = value` to set it")
    #     return val


config = Config(shoreline_dir = Path(__file__).parent / "shoreline_data")

# temp_files_dir = os.path.join(os.path.split(__file__)[0], "temp_files")
temp_files_dir = Path(__file__).parent / "temp_files"
temp_files_dir.mkdir(parents=True, exist_ok=True)

# currents_dir = os.path.join(os.path.split(__file__)[0], "current_sources")

class FileTooBigError(ValueError):
    """Exception for file too big"""

    pass

class NonIntersectingSubsetError(ValueError):
    """
    provided bounds does not overlap with model domain
    """


class NonIntersectingTimeIntervalError(ValueError):
    """
    provided time bounds do not overlap with model time availability
    """


class ModelAvailabilityError(ValueError):
    """
    generic error in model access
    """



