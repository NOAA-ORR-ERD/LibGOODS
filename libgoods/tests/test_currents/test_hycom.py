"""
Test the HYCOM model.

At some point, we could probably write universal tests
"""
from pathlib import Path
from libgoods.currents import get_currents

from libgoods.current_sources.hycom import HYCOM


def test_init():
    hc = HYCOM()

    assert hc.bounding_box == (-78.6, -180, 90, 180)

def test_get_currents():
    """
    testing access throught he top level API
    """
    filename, filepath = get_currents(
        model_name='hycom',
        north_lat=48.874,
        south_lat=48.088,
        west_lon=-125.621,
        east_lon=-124.709,
        cross_dateline=False,
        max_filesize=None,
        )

    print(filename)
    print(filepath)

    # If these got retturned, then we're good.
    assert filename == 'hycom.nc'
    assert filepath
    assert Path(filepath).is_file()



