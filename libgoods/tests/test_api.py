"""
test the top level API
"""

import pytest

from libgoods import api
from shapely.geometry import Polygon

try:
    import model_catalogs

    HAVE_MODEL_CATALOGS = True
except ImportError:
    HAVE_MODEL_CATALOGS = False
    pytest.skip(
        "Can't run these tests without the model_catalogs package",
        allow_module_level=True,
    )


@pytest.mark.skip("don't have actual models to test with")
def test_filter_by_poly_bounds():
    # bounds are expected to only come in (-180, 180)
    testbounds180 = Polygon([(-180, 0), (-180, 10), (-150, 10), (-150, 0)])
    # GFS is 0-360 but the provided bounds should still register intersection
    assert api._filter_by_poly_bounds(api.all_metas["GFS-1_2DEG"], testbounds180)
    # NYOFS is not in the bounds
    assert not api._filter_by_poly_bounds(api.all_metas["NYOFS"], testbounds180)


# def test_filter_by_env_params():
#     pass


# def test_filter_comprehensive():
#     pass
