"""
Test of the base models

Not much here, but at least they can be instantiated.
"""

from libgoods.models import base_models
import libgoods.models as models
from libgoods.models.metadata import Metadata


def test_BaseModel_init():
    bm = base_models.BaseModel()

    assert bm.identifier == "BASE_MODEL"

    assert bm.metadata.name == "An example model"


def test_FVCOM_init():
    """Not testing much, but at least it gets initialized without error"""
    m = base_models.FVCOM()

    assert m.drop_variables == ["Itime", "Itime2"]


def test_ROMS_init():
    """Not testing much, but at least it gets initialized without error"""
    m = base_models.ROMS()

    assert m.tvar == "ocean_time"


def test_models_init():
    """
    not a lot to test -- but at least they all load.
    """
    for key in models.ALL_MODELS:
        print(key)
        m = models.ALL_MODELS[key]()
        assert hasattr(m, "location")
        assert isinstance(m.identifier, str)
        assert isinstance(m.metadata, Metadata)
