from libgoods import maps


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


def test_get_map_dateline():
    """
    tests getting a map that crosses the dateline
    """

    west = 177.0
    east = -156.0
    north = 58.0
    south = 42.0

    # To emulate what the WebAPI does
    bounds = ((west, south),
              (east, north))

    filename, contents = maps.get_map(
        bounds,
        resolution="i",
        cross_dateline=True,
    )

    assert filename == "coast.bna"
    assert len(contents) > 0
    assert contents[:12] == '"Map Bounds"'
    # Are the map bounds correct?
    # header of map gotten from GOODS website:
    header = """"Map Bounds", "2", 4
177.000000, 42.000000
177.000000, 58.000000
204.000000, 58.000000
204.000000, 42.000000
"""
    print(contents[:len(header)])
    assert contents[:len(header)] == header




