"""
Test of the base models

Not much here, but at least they can be instantiated.
"""

from libgoods.models import base_models


def test_BaseModel_init():
    bm = base_models.BaseModel()

    assert bm.metadata.identifier == "BASEMODEL"


def test_FVCOM_init():
    m = base_models.FVCOM()

    assert m.model == "fvcom"


def test_ROMS_init():
    m = base_models.ROMS()

    assert m.model == "roms"
