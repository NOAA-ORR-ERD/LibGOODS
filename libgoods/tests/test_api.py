"""
test the top level API
"""

import pytest

from libgoods import api
from shapely.geometry import Polygon

all_metas = api.all_metas

def test_filter_by_poly_bounds():
    #bounds are expected to only come in (-180, 180)
    testbounds180 = Polygon([(-180, 0), (-180,10), (-150, 10), (-150, 0)])
    #GFS is 0-360 but the provided bounds should still register intersection
    assert api._filter_by_poly_bounds(all_metas['GFS-1_2DEG'], testbounds180)
    #NYOFS is not in the bounds
    assert not api._filter_by_poly_bounds(all_metas['NYOFS'], testbounds180)
    pass

def test_filter_by_name():
    assert api._filter_by_name(all_metas, 'CIOFS')
    

    pass

def test_filter_by_env_params():
    pass

def test_filter_comprehensive():
    pass