"""
tests of the model sub package init
"""

import pytest

from libgoods import models
from libgoods.models.metadata import Metadata


def test_init():
    """
    Just to make sure that some importing is going on
    """
    assert hasattr(models, "WCOFS")


def test_ALL_MODELS():
    """
    not sure what to test here, except BASE_MODEL should not be there
    """
    assert 'BASE_MODEL' not in models.ALL_MODELS


@pytest.mark.parametrize("mod_id", models.ALL_MODELS.keys())
def test_all_models(mod_id):
    """
    testing that all models can be instantiated, and have some basic metadata.
    """
    mod = models.ALL_MODELS[mod_id]()

    assert mod.identifier
    assert isinstance(mod.metadata, Metadata)
    assert mod.metadata.env_params


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


def test_get_model_metadata_all():
    metadata = models.get_model_metadata()

    assert len(metadata) == len(models.ALL_MODELS)


    print(metadata[0])
    assert metadata[0].identifier == "NGOFS2"
    assert metadata[0].env_params == {'3D currents', 'surface currents', 'surface winds', 'water properties'}





