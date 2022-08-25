"""
A set of dummy models that can be used for testing, exploring the API, etc

only one here now, but it would be good to have others
"""

import shutil
from pathlib import Path

from ..model import Model, Metadata
from .. import temp_files_dir


class DummyCurrentsCAROMS(Model):
    """
    A dummy current source -- used hard code small example
    from the CAROMS model
    """

    metadata = Metadata(
        identifier="DUMMY_CUR",
        name="Example currents for testing",
        regional=False,
        bounding_box=((-119.0, 33.0), (-117.5, 34.0)),
        bounding_poly=(
            (-119.0, 33.0),
            (-119.0, 34.0),
            (-118.0, 34.0),
            (-117.5, 33.0),
        ),
        info_text=(
            "Dummy model just for testing, etc.\n"
            "Provides sample output from the CA ROMS model"
        ),
        product_type="hindcast",
        hindcast_start="2021-01-01T19",
        hindcast_end="2022-01-02T19",
        environmental_parameters={"surface currents"},
    )

    def get_available_times(self, cast_type):
        """
        returns the available times for this model as of right now

        :param cast_type: 'forecast' or 'hindcast'

        Hardcoded result
        """
        if cast_type == "forecast":
            return ("2022-01-01T19:00", "2022-01-02T19:00")
        if cast_type == "hindcast":
            return (None, None)

    def get_data(
        self,
        bounds,  # polygon list of (lon, lat) pairs
        time_interval,
        environmental_parameters,
        cross_dateline=False,
        max_filesize=None,
        target_dir=None,
    ):
        super().get_data(
            bounds,  # polygon list of (lon, lat) pairs
            time_interval,
            environmental_parameters,
            cross_dateline,
            max_filesize,
            target_dir,
        )

        dummy_file = Path(__file__).parent / "CAROMS_Example.nc"

        if target_dir is None:
            target_dir = temp_files_dir
        target_file = target_dir / "dummy_current.nc"
        shutil.copy(dummy_file, target_file)

        return target_file


# set up sources dict.

all_dummy_sources = {
    source.metadata.identifier: source() for source in {DummyCurrentsCAROMS}
}
