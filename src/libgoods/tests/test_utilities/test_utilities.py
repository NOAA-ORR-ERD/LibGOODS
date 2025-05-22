"""
Tests  for the libgoods.utilities package
"""

import datetime

import numpy as np
import pytest

from libgoods import utilities
from libgoods.utilities import convert_longitude


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


def test_correct_bbox_for_dateline_not_cross():
    # one that shouldn't change:
    bbox = ((-88, 23), (-87, 24))

    assert bbox == utilities.correct_bbox_for_dateline(bbox)


def test_correct_bbox_for_dateline_did_cross():
    # one that should change:
    bbox = ((-156, 42), (177, 58))

    bbox_fixed = ((177, 42), (-156, 58))

    assert bbox_fixed == utilities.correct_bbox_for_dateline(bbox)


def test_flatten_bbox():
    bbox = ((-88, 23), (-87, 24))
    fbbox = utilities.flatten_bbox(bbox)

    assert fbbox == (-88, 23, -87, 24)


def test_bbox_out_of_model_bounds():
    bad_bbox = (-88, 23, -87, 24)
    model_bdry = [(-130, 42), (-130, 45), (-120, 45), (-120, 42), (-130, 42)]

    assert (
        utilities.subset_intersects_model_boundary(utilities.bbox2polygon(bad_bbox), model_bdry)
        is False
    )


def test_bbox_in_model_bounds():
    good_bbox = (-126, 42.5, -124, 44)
    model_bdry = [(-130, 42), (-130, 45), (-120, 45), (-120, 42), (-130, 42)]

    assert (
        utilities.subset_intersects_model_boundary(utilities.bbox2polygon(good_bbox), model_bdry)
        is True
    )


# Fixme: this is all for global models -- we should special case those instead!
@pytest.mark.parametrize(
    "bbox",
    [
        (0, 0, 10, 10),  # North/East
        (-10, 0, 0, 10),  # North/West
        (-10, -10, 0, 0),  # West/South
        (0, -10, 10, 0),  # West/South
        (-10, 5, 10, 25),  # crossed prime meridian
        (170, -10, 180, 10),  # far east
        (-170, -10, -180, 10),  # far west
        (170, 0, -170, 10),  # crossed dateline
    ],
)
@pytest.mark.parametrize(
    "model_bdry",
    [
        [(0, -80), (0, 90), (360, 90), (360, -80), (0, -80)],
        [(-180, -80), (-180, 90), (180, 90), (180, -80), (-180, -80)],
        #        [(-360, -80), (-360, 90), (0, 90), (0, -80), (-360, -80)], # don't need -360
        [(0.0, -80.0), (0.0, 90.0), (359.999, 90.0), (359.999, -80.0), (0.0, -80.0)],
    ],
)
def test_global_model_bounds(bbox, model_bdry):
    print(bbox)
    print(model_bdry)
    assert (
        utilities.subset_intersects_model_boundary(model_bdry, utilities.bbox2polygon(bbox)) is True
    )


@pytest.mark.parametrize(
    "dt",
    [
        datetime.datetime(2023, 10, 20, 12, 5, 30, 6234),
        datetime.datetime(2023, 10, 20, 11, 30),
        datetime.datetime(2023, 10, 20, 12, 29),
    ],
)
def test_round_dt_to_hours(dt):
    rounded = datetime.datetime(2023, 10, 20, 12)
    dt2 = utilities.round_dt_to_hours(dt)
    assert dt2 == rounded


def test_make_polygon_finer():
    """
    Assume shapely method works, but this will make sure we're getting the right type, etc.
    """
    # use a global bounding box and an example
    poly = ((-180, -90), (-180, 90), (180, 90), (180, -90), (-180, -90))
    poly2 = utilities.make_polygon_finer(poly, threshold=30.0)
    print(poly2)
    print(len(poly2))
    assert len(poly2) == 37
    assert np.array_equal(poly2[0], poly[0])
    assert np.array_equal(poly2[-1], poly[-1])
    assert np.array_equal(poly2[1], [-180.0, -60.0])
    assert np.array_equal(poly2[-2], [-150.0, -90.0])


# #########
# tests for convert_longitude
# #########

L_180_180 = [-180, -179.99999, -90, 0, 90, 179.9999, 180]

L_0_360 = [0, 90, 180, 270, 359.9999, 360]


def test_convert_longitude_bad_input():
    with pytest.raises(TypeError):
        convert_longitude(180_180, "typo")


def test_convert_longitude_360():
    lon = convert_longitude(L_180_180, "0--360")

    assert not np.any(lon >= 360.0)
    assert not np.any(lon < 0.0)


def test_convert_longitude_180():
    lon = convert_longitude(L_0_360)

    print(lon)
    assert not np.any(lon > 180)
    assert not np.any(lon <= -180)


def test_normalization_180():
    lon = convert_longitude(L_180_180)

    print(L_180_180)
    print(lon)

    # only the zeroth element should have changed
    assert np.all(np.array(L_180_180[1:] == lon[1:]))
    assert not np.any(lon > 180)
    assert not np.any(lon <= -180)


def test_normalization_360():
    lon = convert_longitude(L_0_360, "0--360")

    print(L_0_360)
    print(lon)

    # only the last element should have changed
    assert np.all(np.array(L_0_360[:-1] == lon[:-1]))
    assert not np.any(lon < 0)
    assert not np.any(lon >= 360)


def test_round_trip360():
    """
    round tripping should result in the same normalized form
    """
    norm = convert_longitude(L_0_360, "0--360")
    lon = convert_longitude(convert_longitude(L_0_360, "-180--180"), "0--360")

    assert np.all(lon == norm)


def test_round_trip180_180():
    """
    round tripping should result in the same normalized form
    """
    norm = convert_longitude(L_180_180, "-180--180")
    lon = convert_longitude(convert_longitude(L_180_180, "0--360"), "-180--180")

    print(L_180_180)
    print(norm)
    print(lon)
    print(lon == norm)

    assert np.allclose(lon, norm, rtol=1e-15, atol=0)


def test_not_normalize_180():
    assert np.array_equal(convert_longitude((180, -180), "-180--180", normalize=False), (180, -180))


def test_not_normalize_360():
    assert np.array_equal(convert_longitude((0, 360), "0--360", normalize=False), (0, 360))
