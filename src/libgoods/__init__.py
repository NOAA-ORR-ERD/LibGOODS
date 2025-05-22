"""
__init__.py for libgoods package
"""

from pathlib import Path

__version__ = "2.1.0dev"


class FileTooBigError(ValueError):
    """Exception for file too big"""

    pass


# temp_files_dir = os.path.join(os.path.split(__file__)[0], "temp_files")
temp_files_dir = Path(__file__).parent / "temp_files"
temp_files_dir.mkdir(parents=True, exist_ok=True)

# currents_dir = os.path.join(os.path.split(__file__)[0], "current_sources")


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
    provided time bounds do not overlap with model time availability
    """
