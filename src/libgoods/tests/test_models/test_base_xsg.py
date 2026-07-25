"""
tests for the base xsg methods
"""
import xarray as xr

from libgoods.models.base_xsg import XSGBaseModel


def test_parse_time_dim_coords_one(TEST_FILES):
    """
    In the usual case, there is one time coordinate.

    this should return a list of length one.
    """

    # create an empty one, just for testing
    model = XSGBaseModel()

    # give it a minimal example:
    model.ds = xr.open_dataset(TEST_FILES / 'small_fvcom_example.nc')

    model.parse_time_dim_coords()

    assert model.time_dims == ['time']

def test_parse_time_dim_coords_many(TEST_FILES):
    """
    The GFS has multiple time coordinates
    """

    # create an empty one, just for testing
    model = XSGBaseModel()

    # give it a minimal example:
    model.ds = xr.open_dataset(TEST_FILES / 'small_gfs_example.nc')

    model.parse_time_dim_coords()

    assert set(model.time_dims) == {'time','time1', 'time2', 'time3'}

def test_subset_time(TEST_FILES):
    """
    Test with the GFS sample - most complex

    tests that all the time coords are shorter.

    doesn't test that it's actually correct.

    fixme: it would be good to test more thoroughly
    """
    # create an empty one, just for testing
    model = XSGBaseModel()

    # give it a minimal example:
    model.ds = xr.open_dataset(TEST_FILES / 'small_gfs_example.nc')

    first_time = model.ds['time'][2].values
    last_time = model.ds['time'][-2].values

    # get initial lengths of time coords:
    model.parse_time_dim_coords()
    lengths1 = {dim: len(model.ds[dim]) for dim in model.time_dims}
    print(lengths1)

    model.subset_time(first_time, last_time)

    lengths2 = {dim: len(model.ds[dim]) for dim in model.time_dims}
    print(lengths2)

    # only checking that it's shorter, but that's something ...
    for len1, len2 in zip(lengths1.values(), lengths2.values()):
        assert len1 > len2








