"""
Test the TBOFS model.

At some point, we could probably write universal tests
"""
from pathlib import Path

from libgoods.api import get_model_data

from libgoods.current_sources.tbofs import TBOFS


def test_init():
    hc = TBOFS()

    assert hc.metadata.bounding_box == ((-83.172, 27.077), (-82.354, 28.031))


def test_get_metadata():
    md = TBOFS().get_metadata()

    # could check more, but why?
    assert md['name'] == TBOFS.metadata.name
    assert md['product_type'] == "forecast"
    assert md['forecast_start'] != ""
    assert md['forecast_end'] != ""


def test_get_currents():
    """
    testing access through the top level API
    """
    filepath = get_model_data(
                   model_id='TBOFS',
                   bounds=((-82.856, 27.441), (-82.549, 27.714)),
                   # fixme: should test a real time interval!
                   time_interval=('2022-03-02T01:00', '2022-03-03T01:00'),
                   environmental_parameters=['surface currents'],
                   cross_dateline=False,
                   max_filesize=None,
                   target_dir=None
                   )

    # If these got returned, then we're good.
    assert filepath.name == 'tbofs.nc'
    assert Path(filepath).is_file()



