"""
Tests of the shoreline subsetting code -- should be more complete an robust, but it's
something

"""

from pathlib import Path

import numpy as np
import pytest

from libgoods import shoreline
from libgoods.utilities.haz_files import ReadBNA

OUTPUT_DIR = Path(__file__).parent / "output"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def test_get_map_bad_source():
    bounds = (
        -93.5,
        29.6,
        -93.1,
        30.1,
    )
    ofn = OUTPUT_DIR / "junk.bna"

    with pytest.raises(ValueError):
        shoreline.get_map(
            bounds,
            # data_source='gshhs',
            data_source="garbage",
            ofn=ofn,
            resolution="f",  # default is 'h'
            cross_dateline=False,
            max_filesize=1e6,
        )

def test_get_map_specify_source():
    """
    Pass the path to source in directly

    doesn't see if the results are god, but you get something :-)
    """
    # Test with NOS shoreline
    ofn = OUTPUT_DIR / "junk.bna"

    data_source_path = shoreline.shoreline_datasets["nos"]

    bounds = (
        -93.5,
        29.6,
        -93.1,
        30.1,
    )

    # make sure it's not left over from a previous run
    ofn.unlink(missing_ok=True)
    shoreline.get_map(
        bounds,
        # data_source='gshhs',
        data_source=data_source_path,
        ofn=ofn,
        cross_dateline=False,
        max_filesize=1e6,
    )

    assert ofn.is_file()

    polys = ReadBNA(ofn)

    assert len(polys) == 134
    assert polys[0][2] == "Map Bounds"

    assert np.array_equal(
        polys[0][0],
        [
            [-93.5, 29.6],
            [-93.5, 30.1],
            [-93.1, 30.1],
            [-93.1, 29.6],
        ],
    )

# NOTE:
# we should test other datasets, but it takes a bit more setup to do so.
# and nos and gshhs are the "supported" ones at this point.
@pytest.mark.parametrize('source, resolution',
                         [('nos', None),
                          ('gshhs', 'f'),
                          ('gshhs', 'h'),
                          ('gshhs', 'i'),
                          ('gshhs', 'c'),
                          ])
def test_get_map_multiple_sources(source, resolution):
    """
    At least make sure it does something with all these
    sources.
    """
    # Test with NOS shoreline
    # Lake Sabine, for no good reason
    ofn = OUTPUT_DIR / f"{source}_{resolution}.bna"
    # make sure it's not left over from a previous run
    ofn.unlink(missing_ok=True)

    bounds = (
        -93.5,
        29.6,
        -93.1,
        30.1,
    )

    shoreline.get_map(
        bounds,
        data_source=source,
        ofn=ofn,
        resolution=resolution,
        cross_dateline=False,
        max_filesize=1e6,
    )

    assert ofn.is_file()

    polys = ReadBNA(ofn)

    # at least there's a couple land polygons
    assert len(polys) >= 3
    assert polys[0][2] == "Map Bounds"

    assert np.array_equal(
        polys[0][0],
        [
            [-93.5, 29.6],
            [-93.5, 30.1],
            [-93.1, 30.1],
            [-93.1, 29.6],
        ],
    )

def test_get_map_nos():
    """
    At least make sure it works with something ...
    # Test with NOS shoreline
    # Lake Sabine, for no good reason
    """
    ofn = OUTPUT_DIR / "sabine.bna"

    bounds = (
        -93.5,
        29.6,
        -93.1,
        30.1,
    )

    # make sure it's not left over from a previous run
    ofn.unlink(missing_ok=True)
    shoreline.get_map(
        bounds,
        data_source='nos',
        ofn=ofn,
        resolution="f",  # default is 'h'
        cross_dateline=False,
        max_filesize=1e6,
    )

    assert ofn.is_file()

    polys = ReadBNA(ofn)

    assert len(polys) == 134
    assert polys[0][2] == "Map Bounds"

    assert np.array_equal(
        polys[0][0],
        [
            [-93.5, 29.6],
            [-93.5, 30.1],
            [-93.1, 30.1],
            [-93.1, 29.6],
        ],
    )


def test_dateline():
    ofn = OUTPUT_DIR / "cross_dateline.bna"

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
    bounds = (175, 49.0, -175, 56.0)

    # make sure it's not left over from a previous run
    ofn.unlink(missing_ok=True)
    shoreline.get_map(
        bounds,
        data_source="gshhs",
        ofn=ofn,
        resolution="f",  # default is 'h'
        cross_dateline=True,
        max_filesize=1e6,
    )

    assert ofn.is_file()

    polys = ReadBNA(ofn)

    assert len(polys) == 303
    assert polys[0][2] == "Map Bounds"

    # check that it's in 0-360
    lons = []
    for poly in polys:
        lons.extend(poly[0][:, 0])
    lons = np.array(lons)
    assert np.all(lons >= 0)
    assert np.all(lons < 360)


def test_get_map_great_lakes():
    """
    At least make sure it works with something ...
    """
    # Test with GSHHS h shoreline

    # small piec eof lake Erie
    ofn = OUTPUT_DIR / "lake_erie.bna"

    # Decimal latitude, range: ± 90 degrees North Latitude
    # 41.6
    # Decimal longitude, range: ± 180 degrees West Longitude
    # Decimal longitude, range: ± 180 degrees East Longitude
    # Check if subset spans 180th parallel
    # (eg: West Lon = 170, East Lon = -170 Cross dateline?
    # -82.3
    # -82

    # Decimal latitude, range: ± 90 degrees South Latitude
    # 41.4

    bounds = (
        -82.3,
        41.4,
        -82,
        41.6,
    )

    # make sure it's not left over from a previous run
    ofn.unlink(missing_ok=True)
    shoreline.get_map(
        bounds,
        data_source="gshhs",
        # data_source='nos',
        ofn=ofn,
        resolution="h",  # default is 'h'
        cross_dateline=False,
        max_filesize=1e6,
    )

    assert ofn.is_file()

    polys = ReadBNA(ofn)

    assert len(polys) == 3
    assert polys[0][2] == "Map Bounds"
    # could check more, but this should do it.
