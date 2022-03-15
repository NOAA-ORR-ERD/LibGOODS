"""
tests of the data models base class
"""

import pytest

from libgoods.model import Model


def test_Model_get_metadata():
    md = Model().get_metadata()

    print(md.keys())
    assert md.keys() == {'identifier',
                         'name',
                         'bounding_box',
                         'bounding_poly',
                         'info_text',
                         'product_type',
                         'forecast_start',
                         'forecast_end',
                         'hindcast_start',
                         'hindcast_end',
                         'environmental_parameters'
                         }
