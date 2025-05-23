"""
Testing the COOPS ROMS models

So far, only that you can initialize them, and they get the key metadata

"""

import libgoods.models.coops_roms as croms

import pytest

@pytest.mark.parametrize("model_name", [
    'CBOFS',
    'CIOFS',
    'DBOFS',
    'GOMOFS',
    'TBOFS',
    'WCOFS',
])
def test_model_init(model_name):
    """
    Can you initialize it only testing the identifier, but at least it will catch
    the really bad stuff
    """
    print(model_name)
    m = getattr(croms, model_name)()
    print(m)
    print(m.identifier)

    assert m.identifier == model_name
    # maybe test that metadata is not empty?
    print(m.metadata)
    print(m.metadata.name)
    assert m.metadata.name
    assert m.metadata.long_name
    assert m.metadata.bounding_box
    assert m.metadata.bounding_poly


# def test_SSCOFS_init():
#     """
#     Can you initialize it?
#     """
#     m = cfvc.SSCOFS()

#     assert m.identifier == "SSCOFS"
#     assert m.metadata.name == "Salish Sea and Columbia River"
#     assert m.local_file_type == "fields"
#     assert m.standard_names == cfvc.gl_standard_names

