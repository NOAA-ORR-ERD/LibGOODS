"""
Testing the methods in the Base class for models


"""
import xarray as xr
import datetime
import numpy as np
import pandas as pd
from libgoods.models.base_xsg import XSGBaseModel


def make_model():
    lats = np.linspace(40, 50, 40)   # 1/4-degree increments
    lons = np.linspace(-130, -120, 40) # 1/4 degree increments
    times = pd.date_range("2026-01-01", periods=24, freq=datetime.timedelta(hours=3))
    data_shape = (len(times), len(lats), len(lons))
    var_values = 15 + 8 * np.random.randn(*data_shape)
    m = XSGBaseModel()
    m.ds = xr.Dataset(
        data_vars=dict(
            temperature=(["time", "lat", "lon"], var_values),
        ),
        coords=dict(
            lon=lons,
            lat=lats,
            time=times,
        ),
        attrs=dict(description="Example weather data."),
    )
    m.actual_start = times[0].to_pydatetime()
    m.actual_end = times[-1].to_pydatetime()

    return m


def test_parse_time_dim_coords():
    """
    This is simple case - could test GFS for more complicated
    """
    m = make_model()
    m.parse_time_dim_coords()
    assert m.tdim[0] == 'time'


def test_subset_time_exact():
    """
    Test subsetting in time for various overlaps
    """
    m = make_model()
    m.parse_time_dim_coords()

    # test exact match
    start = m.actual_start
    end = m.actual_end
    m.subset_time(start,end)
    assert pd.Timestamp(m.ds['time'].data[0]).to_pydatetime() == start
    assert pd.Timestamp(m.ds['time'].data[-1]).to_pydatetime() == end


def test_subset_time_offset():
    """
    Test subsetting in time for various overlaps
    """
    m = make_model()
    m.parse_time_dim_coords()

    # test start time between second and third value in timeseries
    # time goes 0,3,6 so this should yield 3
    start = m.actual_start + datetime.timedelta(hours=5)
    m.subset_time(start, None)
    assert pd.Timestamp(m.ds['time'].data[0]).to_pydatetime() == \
        datetime.datetime(2026, 1, 1, 3)

    end = m.actual_end - datetime.timedelta(hours=5)
    m.subset_time(None, end)
    assert pd.Timestamp(m.ds['time'].data[-1]).to_pydatetime() == \
        datetime.datetime(2026, 1, 3, 18)