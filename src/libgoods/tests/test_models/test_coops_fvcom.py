from libgoods.models.coops_fvcom import NGOFS2


def test_NGOFS2_init():
    """
    Can you initialize it?
    """
    m = NGOFS2()

    assert m.metadata.name == "NOAA/NOS Northern Gulf of America Operational Forecast System"
