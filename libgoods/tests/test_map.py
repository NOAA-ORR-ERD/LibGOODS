from libgoods import maps, utilities
import pytest


def test_get_map():
    """
    A single map request
    """
    bounds = (
        (-124.26942110656861, 46.78488364986247),
        (-123.6972360021842, 47.06693175688763),
    )

    filename, contents = maps.get_map(
        bounds,
        resolution="i",
        cross_dateline=False,
    )

    assert filename == "coast.bna"
    assert len(contents) > 0
    assert contents[:12] == '"Map Bounds"'
