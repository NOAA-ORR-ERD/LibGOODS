from libgoods.models.dummy_models import DummyGlobalModel, DummyRegionalModel


def test_dummy_regional_model_init():
    m = DummyRegionalModel()

    print(m)
    assert m.identifier == "DUMREG"
    # not testing much, but something??
    assert len(m.metadata.bounding_poly) == 12


def test_dummy_global_model_init():
    m = DummyGlobalModel()

    print(m)
    assert m.identifier == "DUMGLOB"
    assert len(m.metadata.bounding_poly) == 4
