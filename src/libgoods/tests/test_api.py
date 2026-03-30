"""
Test the top level API
"""

import datetime

import pytest

from libgoods import (
#    ModelAvailabilityError,
    NonIntersectingSubsetError,
    NonIntersectingTimeIntervalError,
    api,
    utilities,
)


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
    # Fixme: This isn't really a test of the API code per se.
    #        The underlying functionality should be tested elsewhere.
    m = api.get_model(model_id="TBOFS") # arbitrary choice

    assert hasattr(m.metadata, 'actual_start')
    assert hasattr(m.metadata, 'actual_end')


class Test_validate_subset:
    # out of bounds except for global model
    bad_bounds =  [(-180, 10), (-150, 10), (-150, 0), (-180, 0)]
    good_bounds = [(-83.0, 28.0), (-83.0, 27.5), (-82.0, 27.5), (-82.0, 28.0)]
    start = datetime.datetime.today()
    model_id = 'TBOFS'

    def test_non_intersecting(self):
        end = self.start + datetime.timedelta(days=1)
        model_id = 'TBOFS'
        with pytest.raises(NonIntersectingSubsetError):
            api.validate_subset(model_id, self.start, end, self.bad_bounds)

    def test_good(self):
        model_id = 'TBOFS'
        end = self.start + datetime.timedelta(days=1)
        assert api.validate_subset(model_id, self.start, end, self.good_bounds)

    def test_bad_time(self):
        model_id = 'TBOFS'
        start = self.start + datetime.timedelta(days=365)
        end = self.start + datetime.timedelta(days=1)
        with pytest.raises(NonIntersectingTimeIntervalError):
            api.validate_subset(model_id, start, end, self.good_bounds)

@pytest.mark.skip(reason="This causes it to hang -- ESPC model bad?")
def test_get_model_subset():
    """
    THis really needs refactoring!
    """
    #get a very small subset - nothing specific to check except it "works"
    model_id = 'ESPC'
    start = datetime.datetime.today()
    end = start + datetime.timedelta(days=0.5)
    bounds = [(-171, 1), (-170, 1), (-170, 0), (-171, 0)]
    model_obj = api.get_model_subset(model_id, start, end, bounds)

    # We Really should test for something real
    assert hasattr(model_obj,'ds')


# Move this test to utilities? Its a crossover between api and utilities
# I left it here for now since I got it working
# @pytest.mark.skip(reason="This causes it to hang -- ESPC model bad?")
def test_filter_by_poly_bounds():
    # bounds are expected to only come in (-180, 180)
    testbounds180 = [(-180, 0), (-180, 10), (-150, 10), (-150, 0)]
    # ESPC is 0-360 but the provided bounds should still register intersection
    meta = api.list_models(model_ids = ['ESPC'])[0]
    assert utilities.subset_intersects_model_boundary(meta["bounding_poly"], testbounds180)
    # TBOFS is not in the bounds
    meta = api.list_models(model_ids = ['TBOFS'])[0]
    assert not utilities.subset_intersects_model_boundary(meta["bounding_poly"], testbounds180)

