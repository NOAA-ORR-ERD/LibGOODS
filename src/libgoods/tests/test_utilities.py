"""
Tests  for the libgoods.utilities package
"""

import datetime

from libgoods import utilities
import pytest


@pytest.mark.parametrize("lat", [45, -45, 0])
def test_check_check_valid_latitude_valid(lat):
    assert utilities.check_valid_latitude(lat)


@pytest.mark.parametrize("lat", [-90.0001, 90.0001])
def test_check_check_valid_latitude_invalid(lat):

    with pytest.raises(ValueError):
        utilities.check_valid_latitude(lat)


@pytest.mark.parametrize("lat", [-180, 180, 360])
def test_check_check_valid_longitude_valid(lat):
    assert utilities.check_valid_longitude(lat)


@pytest.mark.parametrize("lat", [-180.001, 360.0001])
def test_check_check_valid_longitude_invalid(lat):

    with pytest.raises(ValueError):
        utilities.check_valid_longitude(lat)


def test_check_valid_box_good():
    bbox = ((-88, 23), (-87, 24))
    assert utilities.check_valid_box(bbox) is True


def test_check_valid_box_bad():
    """
    only one check, as the underlying code should already be checked
    """
    bbox = ((-88, 91), (-87, 24))
    with pytest.raises(ValueError):
        utilities.check_valid_box(bbox)


def test_polygon2bbox_good():
    bounds = [(-130, 45), (-130, 50), (-125, 50), (-125, 45)]
    bbox = utilities.polygon2bbox(bounds)
    assert bbox == ((-130, 45), (-125, 50))


@pytest.mark.parametrize(
    "bounds",
    [
        [(-130, 45)],
        [(-130, 45), (-130, 50), (-125), (-125, 45)],
    ],
)  # noqa
def test_polygon2bbox_bad(bounds):

    with pytest.raises(ValueError):
        bbox = utilities.polygon2bbox(bounds)  # noqa


def test_bbox2polygon():

    bbox = (-88, 23, -87, 24)
    bounds = utilities.bbox2polygon(bbox)

    assert bounds == [(-88, 24), (-87, 24), (-87, 23), (-88, 23)]


def test_flatten_bbox():

    bbox = ((-88, 23), (-87, 24))
    fbbox = utilities.flatten_bbox(bbox)

    assert fbbox == (-88, 23, -87, 24)


def test_bbox_out_of_model_bounds():

    bad_bbox = (-88, 23, -87, 24)
    model_bdry = [(-130, 42), (-130, 45), (-120, 45), (-120, 42), (-130, 42)]

    assert utilities.subset_intersects_model_boundary(
        utilities.bbox2polygon(bad_bbox), model_bdry) is False


def test_bbox_in_model_bounds():

    good_bbox = (-126, 42.5, -124, 44)
    model_bdry = [(-130, 42), (-130, 45), (-120, 45), (-120, 42), (-130, 42)]

    assert utilities.subset_intersects_model_boundary(
        utilities.bbox2polygon(good_bbox), model_bdry) is True

def test_weird_model_bounds():
    bboxs = [(0, 0, 10, 10), #North/East
             (-10, 0, 0, 10), #North/West
             (-10, -10, 0, 0),
             (0, -10, 10, 0),
             (-190, 0, 170, 10), #crosses dateline
             (170, 0, 190, 10),
             (170, 0, -170, 10)
    ]
    
    model_bdrys = [
        [(0, -80), (0, 90), (360, 90), (360, -80), (0, -80)],
        [(-180, -80), (-180, 90), (180, 90), (180, -80), (-180, -80)],
        [(-360, -80), (-360, 90), (0, 90), (0, -80), (-360, -80)],
        [(0.0, -80.0),(0.0, 90.0),(359.92, 90.0),(359.92, -80.0),(0.0, -80.0)]
    ]
    
    for bbox in bboxs:
        for model_bdry in model_bdrys:
            assert utilities.subset_intersects_model_boundary(model_bdry,
                utilities.bbox2polygon(bbox)) is True


@pytest.mark.parametrize('dt', [datetime.datetime(2023, 10, 20, 12, 5, 30, 6234),
                                datetime.datetime(2023, 10, 20, 11, 30),
                                datetime.datetime(2023, 10, 20, 12, 29),
                                ])
def test_round_dt_to_hours(dt):
    rounded = datetime.datetime(2023, 10, 20, 12)
    dt2 = utilities.round_dt_to_hours(dt)
    assert dt2 == rounded


