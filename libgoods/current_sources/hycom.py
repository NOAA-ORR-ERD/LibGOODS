"""
HYCOM global ocean model
"""
import os
from ..data_model import DataSource, Metadata
from .. import temp_files_dir
from ..file_processing import rect
from ..utilities import polygon2bbox


# fixme: we probably don't want actual HTML in there
#        but if so -- some sanitation needs to be done.
INFO_TEXT = """The global HYbrid Coordinate Ocean Model (HYCOM)
nowcast/forecast system is a demonstration product of the
<a href = "http://www.hycom.org" target="_blank">HYCOM Consortium</a>
run in real time at the Naval Oceanographic Office.
For more details about the global model visit the
<a href="http://www7320.nrlssc.navy.mil/GLBhycom1-12/prologue.html" target="_blank"> global HYCOM website</a>.",
"""


# using the "old libgoods" classes as a mixin to get
# the existing functionality
class HYCOM(DataSource, rect):
    """
    global HYCOM
    """

    metadata = Metadata(
        identifier="HYCOM",
        name="Global Ocean Forecasting System (GOFS) 3.1",
        bounding_box=((-180, -78.6), (180, 90)),
        bounding_poly=((-78.6, -180.0), (90.0, -180.0), (90.0, 180.0), (-78.6, 180.0)),
        info_text=INFO_TEXT,
        forecast_available=True,
        hindcast_available=False,
        environmental_parameters={
            "surface currents",
            "sea surface temperature",
            "ice data",
            "3D currents",
        },
    )

    # needed for internal processing
    url = "https://tds.hycom.org/thredds/dodsC/GLBy0.08/expt_93.0/FMRC/GLBy0.08_930_FMRC_best.ncd"
    var_map = {
        "time": "time",
        "lon": "lon",
        "lat": "lat",
        "z": "depth",
        "u": "water_u",
        "v": "water_v",
    }
    default_filename = "hycom.nc"

    def __init__(self):
        """initialize a HYCOM instance"""
        # we may need to query this object before actually
        # opening a OpeNDap session -- so not doing this now.

        # self.open_nc(FileName=self.url)

    def get_available_times(self):
        """
        returns the available times for this model as of right now

        hard-coded for now -- needs to be fixed!
        """
        return ("2022-01-17T22:00Z", "2022-01-20T22:00Z")

    def get_data(
        self,
        bounds,
        time_interval,
        environmental_parameters,
        cross_dateline=False,
        max_filesize=None,
        target_dir=None,
    ):
        """
        wrapping this so we can open the opendap connection
        right before querying the data
        """
        # not using super() because the base classes are not compatible.
        DataSource.get_data(
            self,
            bounds,  # polygon list of (lon, lat) pairs
            time_interval,
            environmental_parameters,
            cross_dateline,
            max_filesize,
            target_dir,
        )

        self.open_nc(FileName=self.url)

        filepath = rect.get_data(self, bounds, cross_dateline, max_filesize, target_dir)

        return filepath
