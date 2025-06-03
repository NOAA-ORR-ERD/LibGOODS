"""
Not fully tested, but it's something ....
"""

from libgoods import NWS_point

import pytest

@pytest.mark.skip(reason="doesn't appear to be working now ...")
def test_get_data():
    """
    tricky, as this requires hitting the server ...
    """
    lon, lat =  -89.041667, 29.208333  # somewhere in the MR delta

    data = NWS_point.get_data(lon, lat)

    print(data)

    assert False


def test_format_OSSM():
    pass



