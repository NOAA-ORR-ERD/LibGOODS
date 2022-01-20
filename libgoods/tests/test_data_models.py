"""
tests of the data models base class
"""

import pytest

from libgoods.data_models import DataSource

def test_DataSource_get_metadata():
    md = DataSource.get_metadata()

    print(md)
    for key in ('name', 'data_type', 'bounding_box', 'bounds', 'info_text'):
        assert key in md
