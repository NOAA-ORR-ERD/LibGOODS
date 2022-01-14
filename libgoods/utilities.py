"""
assorted utilities useful for libgoods
"""

def check_valid_latitude(lat):

    if -90 < lat > 90:
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
    if -180 < lat > 360:
        raise ValueError(
            f'longitude cannot be larger than 360 or less than -180. Got{lon}')

    return True
