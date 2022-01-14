"""
tests  for the libgoods.utilities package
"""

from libgoods import utilities


def test_check_check_valid_latitude_valid():
    lat = 45

    assert utilities.check_valid_latitude(lat)

def test_check_check_valid_latitude_invalid():
    lat = 91

    with pytest.raises(ValueError):
        utilities.check_valid_latitude(lat)
