from libgoods.models.coops_fvcom import NGOFS2, SSCOFS


def test_NGOFS2_init():
    """
    Can you initialize it?
    """
    m = NGOFS2()

    assert m.identifier == "NGOFS2"
    assert m.metadata.name == "Northern Gulf of America"

def test_SSCOFS_init():
    """
    Can you initialize it?
    """
    m = SSCOFS()

    assert m.identifier == "SSCOFS"
    assert m.metadata.name == "Northern Gulf of America"
    assert m.local_file_type == "fields"
    assert m.standard_names == gl_standard_names
