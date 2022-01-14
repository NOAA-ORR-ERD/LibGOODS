"""
__init__.py for libgoods package
"""

__version__ = "0.0.1"

# find data_files
import os

temp_files_dir = os.path.join(os.path.split(__file__)[0], "temp_files")
currents_dir = os.path.join(os.path.split(__file__)[0], "currents")
if not os.path.exists(temp_files_dir):
    os.mkdir(temp_files_dir)

