import pytest

import libgoods.models.coops_fvcom as cfvc


def test_NGOFS2_init():
    """
    Can you initialize it?
    """
    m = cfvc.NGOFS2()

    assert m.identifier == "NGOFS2"
    assert m.metadata.name == "Northern Gulf of America"
    assert m.metadata.env_params == {
        '3D currents', 'surface currents', 'surface winds', 'water properties'
    }


def test_SSCOFS_init():
    """
    Can you initialize it?
    """
    m = cfvc.SSCOFS()

    assert m.identifier == "SSCOFS"
    assert m.metadata.name == "Salish Sea and Columbia River"
    assert m.local_file_type == "fields"
    assert m.metadata.env_params == {
        '3D currents', 'surface currents', 'surface winds', 'water properties'
    }


@pytest.mark.parametrize(
    "model_name",
    [
        #    "SSCOFS",
        "NGOFS2",
        "LEOFS",
        "LMHOFS",
        "LOOFS",
        "LSOFS",
    ])
def test_model_init(model_name):
    """
    Can you initialize it only testing the identifier, but at least it will catch
    the really bad stuff
    """
    print(model_name)
    m = getattr(cfvc, model_name)()

    assert m.identifier == model_name
    assert m.metadata.name
    assert m.metadata.long_name
    assert m.metadata.bounding_box
    assert m.metadata.bounding_poly
