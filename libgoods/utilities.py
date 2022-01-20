"""
assorted utilities useful for libgoods
"""
import numpy as np

def check_valid_latitude(lat):

    if not (-90.0 < lat < 90.0):
        raise ValueError(f'latitude cannot be larger than 90. Got{lat}')

    return True


def check_valid_longitude(lon, system='all'):
    """
    checks for valid longitude coordinates.

    Only option is 'all': -180 -- 360

    We should impliment other options some day:
     - -180 -- 180
     - 0 -- 360
    """
    COORDSYSTEMS = {'all'}
    if system not in {'all'}:
        raise ValueError(f'Invalid coordinate system. Options are: {COORDSYSTEMS}')
    if not (-180.0 <= lon <= 360.0):
        raise ValueError(
            f'longitude cannot be larger than 360 or less than -180. Got{lon}')

    return True


def shift_lon_coords(coords, system):
    """
    shift longitude to the defined system
    """

def detect_lon_coords(coords, system):
    """
    detects the longitude coords system

     - -180 -- 180
     - 0 -- 360
    """

def polygon2bbox(bounds):
    """
    converts four points to a four value tuple defining a bounding box.

    In the form: (min_lat, min_lon, max_lat, max_lon)
    """

    if len(bounds) != 4:
        raise ValueError('Bounding box must be 4 points')

    try:
        bounds = np.asarray(bounds, dtype=np.float64)
    except ValueError as err:
        raise ValueError("bounds must be 4 pairs of (lon, lat) points") from err
    min_lon, min_lat = bounds.min(axis=0)
    max_lon, max_lat = bounds.max(axis=0)
    return (min_lat, min_lon, max_lat, max_lon)


def bbox2polygon(bbox):
    """
    Converts four points in the form:
    (min_lat, min_lon, max_lat, max_lon)

    To a four point polygon:
    """

    min_lat, min_lon, max_lat, max_lon = bbox
    return [(min_lon, max_lat),
            (max_lon, max_lat),
            (max_lon, min_lat),
            (min_lon, min_lat)]

