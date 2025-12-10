"""
Test the top level API


"""

import pytest
from libgoods import api, utilities, NonIntersectingSubsetError, NonIntersectingTimeIntervalError, ModelAvailabilityError
import datetime


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


def test_get_model_info_no_archive():
    """
    This uses a COOPS source that defaults to zarr aggregation - reliant on that working
    """
    m = api.get_model(model_id="TBOFS") # arbitrary choice

    assert 'actual_start' in m.metadata
    assert 'actual_end' in m.metadata


def test_validate_subset():
    test_bounds =  [-180, 0, -150, 10] #out of bounds except for global model
    start = datetime.datetime.today()
    end = start + datetime.timedelta(days=1)
    model_id = 'TBOFS'
    with pytest.raises(NonIntersectingSubsetError):
        api.validate_subset(model_id, start, end, test_bounds)
    model_id = 'ESPC'
    assert api.validate_subset(model_id, start, end, test_bounds)
    start = start + datetime.timedelta(days=365)
    end = start + datetime.timedelta(days=1)
    with pytest.raises(NonIntersectingTimeIntervalError):
        api.validate_subset(model_id, start, end, test_bounds)

def test_get_model_subset():
    #get a very small subset - nothing specific to check except it "works"
    model_id = 'ESPC'
    start = datetime.datetime.today()
    end = start + datetime.timedelta(days=0.5)
    bounds = [-171, 0, -170, 1]
    try:
        ds = api.get_model_subset(model_id, start, end, bounds)
    except:
        raise ModelAvailabilityError('Creating subset failed - could be TDS issue but should verify')

# Move this test to utilities? Its a crossover between api and utilities
# I left it here for now since I got it working
def test_filter_by_poly_bounds():
    # bounds are expected to only come in (-180, 180)
    testbounds180 = [(-180, 0), (-180, 10), (-150, 10), (-150, 0)]
    # ESPC is 0-360 but the provided bounds should still register intersection
    meta = api.list_models(model_ids = ['ESPC'])[0]
    assert utilities.subset_intersects_model_boundary(meta["bounding_poly"], testbounds180)
    # TBOFS is not in the bounds
    meta = api.list_models(model_ids = ['TBOFS'])[0]
    assert not utilities.subset_intersects_model_boundary(meta["bounding_poly"], testbounds180)

