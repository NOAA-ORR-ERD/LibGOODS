"""
Test the Dummy currents

"""
from pathlib import Path

from libgoods.data_sources import get_model_data

from libgoods.dummy_sources import DummyCurrentsCAROMS


def test_init():
    dc = DummyCurrentsCAROMS()

    assert dc.metadata.bounding_box == ((-119.0, 33.0), (-117.5, 34.0))


def test_get_metadata():
    md = DummyCurrentsCAROMS().get_metadata()

    # could check more, but why?
    assert md["name"] == DummyCurrentsCAROMS.metadata.name
    assert md["forecast_available"] is True
    assert md["hindcast_available"] is False


def test_get_model_data():
    """
    testing access through the top level API
    """
    filepath = get_model_data(
        model_id="dummy_cur",
        bounds=(
            (-119.0, 33.0),
            (-119.0, 34.0),
            (-118.0, 34.0),
            (-118.0, 33.0),
        ),
        time_interval=("2022-02-15T12:00", "2022-04-15T12:00"),
        environmental_parameters=["surface currents"],
        cross_dateline=False,
        target_dir=None,
    )


    # If these got returned, then we're good.
    assert filepath.name == "dummy_current.nc"
    assert Path(filepath).is_file()
