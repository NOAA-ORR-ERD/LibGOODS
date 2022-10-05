"""
Test the Dummy currents

"""

import pytest

pytest.skip("Skipping -- obsolete", allow_module_level=True)

from pathlib import Path

from libgoods.api import get_model_data

from libgoods.dummy_sources import DummyCurrentsCAROMS

HERE = Path(__file__).parent


def test_init():
    dc = DummyCurrentsCAROMS()

    assert dc.metadata.bounding_box == ((-119.0, 33.0), (-117.5, 34.0))


def test_get_metadata():
    md = DummyCurrentsCAROMS().get_metadata()

    # could check more, but why?
    assert md["name"] == DummyCurrentsCAROMS.metadata.name
    assert md["product_type"] is "hindcast"
    # just checking it there, not the values
    assert md["hindcast_start"] != ""
    assert md["hindcast_end"] != ""


def test_get_model_data():
    """
    testing access through the top level API
    """
    filepath = get_model_data(
        model_id="DUMMY_CUR",
        bounds=(
            (-119.0, 33.0),
            (-119.0, 34.0),
            (-118.0, 34.0),
            (-118.0, 33.0),
        ),
        time_interval=("2022-02-15T12:00", "2022-04-15T12:00"),
        environmental_parameters=["surface currents"],
        cross_dateline=False,
        target_dir=HERE,
    )

    # If these got returned, then we're good.
    assert filepath.name == "dummy_current.nc"
    assert filepath.is_file()
    assert filepath == HERE / "dummy_current.nc"
