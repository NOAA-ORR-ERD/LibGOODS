"""
tests  for the libgoods.utilities package
"""

from libgoods import utilities

import pytest


@pytest.mark.parametrize('lat', [45, -45, 0])
def test_check_check_valid_latitude_valid(lat):
    assert utilities.check_valid_latitude(lat)


@pytest.mark.parametrize('lat', [-90.0001, 90.0001])
def test_check_check_valid_latitude_invalid(lat):

    with pytest.raises(ValueError):
        utilities.check_valid_latitude(lat)


@pytest.mark.parametrize('lat', [-180, 180, 360])
def test_check_check_valid_longitude_valid(lat):
    assert utilities.check_valid_longitude(lat)


@pytest.mark.parametrize('lat', [-180.001, 360.0001])
def test_check_check_valid_longitude_invalid(lat):

    with pytest.raises(ValueError):
        utilities.check_valid_longitude(lat)
