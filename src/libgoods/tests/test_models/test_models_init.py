"""
tests of the model sub package init
"""

from libgoods import models


def test_init():
    """
    Just to make sure that some importing is going on
    """
    assert hasattr(models, "WCOFS")


def test_get_models():
    """
    Not much to test here, but at least it returns something
    """
    mods = models.get_models()

    print(mods)
    # at least it's not empty
    assert mods
    assert isinstance(mods[0][0], str)
    assert isinstance(mods[0][1], str)
