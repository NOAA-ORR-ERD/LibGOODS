"""
test the top level API

What the Heck? no tests at all???
"""

import pytest
from shapely.geometry import Polygon

from libgoods import api


def test_list_models():
    """
    just testing the main list metadata with no filtering
    """
    # This gets then all, with no filter
    models = api.list_models()

    print(f"got: {len(models)} models")

    print(type(models[0]))
    print(models[0]['identifier'])

    # what else to test??
    for m in models:
        assert isinstance(m, dict)
        assert m['identifier']


@pytest.mark.skip("don't have actual models to test with")
def test_filter_by_poly_bounds():
    # bounds are expected to only come in (-180, 180)
    testbounds180 = Polygon([(-180, 0), (-180, 10), (-150, 10), (-150, 0)])
    # GFS is 0-360 but the provided bounds should still register intersection
    assert api._filter_by_poly_bounds(api.all_metas["GFS-1_2DEG"], testbounds180)
    # NYOFS is not in the bounds
    assert not api._filter_by_poly_bounds(api.all_metas["NYOFS"], testbounds180)


def test_get_model_info_no_archive():
    """
    at least something ...
    """
    mi = api.get_model_info(model_id="WFCOM") # arbitrary choice

    assert 'actual_start' in mi
    assert 'actual_end' in mi





# def test_filter_by_env_params():
#     pass


# def test_filter_comprehensive():
#     pass
