"""
Test the HYCOM model.

At some point, we could probably write universal tests
"""

import pytest
pytest.skip("Skipping -- obsolete", allow_module_level=True)


from pathlib import Path

from libgoods.api import get_model_data

from libgoods.current_sources.hycom import HYCOM

HERE = Path(__file__).parent


def test_init():
    hc = HYCOM()

    assert hc.metadata.bounding_box == ((-180, -78.6), (180, 90))


def test_get_metadata():
    md = HYCOM().get_metadata()

    # could check more, but why?
    assert md['name'] == HYCOM.metadata.name
    assert md['product_type'] == "forecast"
    assert md['forecast_start'] != ""
    assert md['forecast_end'] != ""


def test_get_currents():
    """
    testing access through the top level API
    """
    filepath = get_model_data(
                   model_id='HYCOM',
                   bounds=((-125.621, 48.088), (-124.709, 48.874)),
                   # fixme: should test a real time interval!
                   time_interval=('2022-02-15T12:00', '2022-04-15T12:00'),
                   environmental_parameters=['surface currents'],
                   cross_dateline=False,
                   max_filesize=None,
                   target_dir=HERE,
                   )

    # If these got returned, then we're good.
    assert filepath.name == 'hycom.nc'
    assert filepath.is_file()
    assert filepath == HERE / 'hycom.nc'
