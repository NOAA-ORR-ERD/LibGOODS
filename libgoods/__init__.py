"""
__init__.py for libgoods package
"""

from pathlib import Path

__version__ = "2.0.1"

import os


class FileTooBigError(ValueError):
    """class for file too big"""

    pass


# temp_files_dir = os.path.join(os.path.split(__file__)[0], "temp_files")
temp_files_dir = Path(__file__).parent / "temp_files"
temp_files_dir.mkdir(parents=True, exist_ok=True)

# currents_dir = os.path.join(os.path.split(__file__)[0], "current_sources")
