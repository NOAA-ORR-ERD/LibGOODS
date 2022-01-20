from libgoods import maps
import pytest


def test_get_map():
    """
    A single map request
    """
    filename, contents = maps.get_map(
        north_lat=47.06693175688763,
        south_lat=46.78488364986247,
        west_lon=-124.26942110656861,
        east_lon=-123.6972360021842,
        resolution='i',
        cross_dateline=False,
    )

    assert filename == 'coast.bna'
    assert len(contents) > 0
    assert contents[:12] == '"Map Bounds"'
