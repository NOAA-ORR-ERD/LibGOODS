"""
Tests  for the libgoods.utilities package
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


def test_polygon2bbox_good():
    bounds = [(-130, 45), (-130, 50), (-125, 50), (-125, 45)]
    bbox = utilities.polygon2bbox(bounds)
    assert bbox == (45, -130, 50, -125)


@pytest.mark.parametrize('bounds', [
    [(-130, 45), (-130, 50), (-125, 50)],
    [(-130, 45), (-130, 50), (-125, 50), (-125, 45), (-125, 45)],
    [(-130, 45), (-130, 50), (-125), (-125, 45)],
     ])  # noqa
def test_polygon2bbox_bad(bounds):

    with pytest.raises(ValueError):
        bbox = utilities.polygon2bbox(bounds)  # noqa


def test_bbox2polygon():

    bbox = (23, -88, 24, -87)
    bounds = utilities.bbox2polygon(bbox)

    assert bounds == [(-88, 24), (-87, 24), (-87, 23), (-88, 23)]

