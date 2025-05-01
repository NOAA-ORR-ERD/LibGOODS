"""
Tests of the shoreline subsetting code -- should be more complete an robust, but it's
something

"""
from pathlib import Path

from libgoods import shoreline

OUTPUT_DIR = Path(__file__).parent / "output"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def test_get_map():
    """
    At least make sure it works with something ...
    """
    # Test with NOS shoreline
    # Lake Sabine, for no good reason
    ofn = OUTPUT_DIR / 'sabine.bna'

    bounds = (-93.5, 29.6, -93.1, 30.1,
              )

    # make sure it's not left over from a previous run
    ofn.unlink(missing_ok=True)
    shoreline.get_map(bounds,
                      # data_source='gshhs',
                      data_source='nos',
                      ofn=ofn,
                      resolution='f', # default is 'h'
                      cross_dateline=False,
                      max_filesize=1e6)

    assert ofn.is_file()

    contents = open(ofn).read()

    # not much of a test, but it means it was written
    assert '"Map Bounds", "2", 4' in contents


def test_dateline():
    # Test with NOS shoreline
    # Lake Sabine, for no good reason
    ofn = OUTPUT_DIR / 'cross_dateline.bna'

    # 175.000000, 49.000000
    # 175.000000, 56.000000
    # 185.000000, 56.000000
    # 185.000000, 49.000000


    # # webgnome request:
    # NorthLat: 54.849899941695725
    # WestLon: 173.86036250611824
    # EastLon: -171.6426512869359
    # SouthLat: 48.55779647087085

    # result is in 0-360
    # even when crossing dateline, use -180--180 coords
    bounds = (175, 49.0,
              -175, 56.0)

    # make sure it's not left over from a previous run
    ofn.unlink(missing_ok=True)
    shoreline.get_map(bounds,
                      data_source='gshhs',
                      ofn=ofn,
                      resolution='f', # default is 'h'
                      cross_dateline=True,
                      max_filesize=1e6)

    assert ofn.is_file()

    contents = open(ofn).read()

    # not much of a test, but it means it was written
    assert '"Map Bounds", "2", 4' in contents


