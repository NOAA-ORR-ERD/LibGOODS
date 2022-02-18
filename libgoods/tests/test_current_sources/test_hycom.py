"""
Test the HYCOM model.

At some point, we could probably write universal tests
"""
from pathlib import Path

from libgoods.data_sources import get_model_data

from libgoods.current_sources.hycom import HYCOM


def test_init():
    hc = HYCOM()

    assert hc.metadata.bounding_box == (-78.6, -180, 90, 180)


def test_get_metadata():
    md = HYCOM().get_metadata()

    # could check more, but why?
    assert md['name'] == HYCOM.metadata.name
    assert md['forecast_available'] is True


def test_get_currents():
    """
    testing access through the top level API
    """
    filepath = get_model_data(
                   model_id='hycom',
                   bounds=((-125.621, 48.088), (-124.709, 48.874)),
                   # fixme: should test a real time interval!
                   time_interval=('2022-02-15T12:00', '2022-04-15T12:00'),
                   environmental_parameters=['surface currents'],
                   cross_dateline=False,
                   max_filesize=None,
                   target_dir=None
                   )

    # If these got returned, then we're good.
    assert filepath.name == 'hycom.nc'
    assert Path(filepath).is_file()



