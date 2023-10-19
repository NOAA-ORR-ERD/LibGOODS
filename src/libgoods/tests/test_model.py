"""
tests of the data models base class (file_processing/base)
"""
import pytest
from libgoods.file_processing import base
import datetime
from netCDF4 import num2date
import numpy as np

model = base.nc()

model.time_units = 'hours since 2023-06-01 00:00'
model.time = np.arange(0, 72)


def test_get_timeslice_indices_valid():

    start = datetime.datetime(2023, 6, 1, 0, 0)
    end = datetime.datetime(2023, 6, 3, 23, 0)
    t_ind = model.get_timeslice_indices(start, end)

    assert num2date(model.time, model.time_units)[t_ind[0]] == start
    assert num2date(model.time, model.time_units)[t_ind[-1]] == end


def test_get_timeslice_indices_before_range():

    start = datetime.datetime(2021, 6, 1, 0, 0)
    end = datetime.datetime(2021, 6, 3, 23, 0)
    with pytest.raises(ValueError):
        t_ind = model.get_timeslice_indices(start, end)


def test_get_timeslice_indices_valid():

    start = datetime.datetime(2023, 6, 1, 0, 0)
    end = datetime.datetime(2023, 6, 3, 23, 0)
    t_ind = model.get_timeslice_indices(start, end)

    assert num2date(model.time, model.time_units)[t_ind[0]] == start
    assert num2date(model.time, model.time_units)[t_ind[-1]] == end


def test_get_timeslice_indices_after_range():

    start = datetime.datetime(2027, 6, 1, 0, 0)
    end = datetime.datetime(2027, 6, 3, 23, 0)
    with pytest.raises(ValueError):
        t_ind = model.get_timeslice_indices(start, end)


def test_get_timeslice_indices_overlap():

    start = datetime.datetime(2023, 5, 31, 0, 0)
    end = datetime.datetime(2027, 6, 5, 23, 0)
    t_ind = model.get_timeslice_indices(start, end)

    assert t_ind[0] == 0
    assert t_ind[1] == len(model.time) - 1
