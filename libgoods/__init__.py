"""
__init__.py for libgoods package
"""

__version__ = "0.0.2"

# find data_files
import os

class FileTooBigError(ValueError):
    pass


temp_files_dir = os.path.join(os.path.split(__file__)[0], "temp_files")
currents_dir = os.path.join(os.path.split(__file__)[0], "current_sources")
if not os.path.exists(temp_files_dir):
    os.mkdir(temp_files_dir)


