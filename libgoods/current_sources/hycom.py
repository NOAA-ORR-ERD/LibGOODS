"""
HYCOM global ocean model
"""
import os
from ..data_models import Currents
from .. import rect_model, temp_files_dir
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


# using the "old libgoods" classes as a mixing to get
# the exsisting functionality
class HYCOM(Currents, rect_model.rect):
    """
    global HYCOM
    """
    # metadata for HYCOM

    name = "Global Ocean Forecasting System (GOFS) 3.1"
    data_type = 'currents'
    info_text = INFO_TEXT
    bounding_box = (-78.6, -180, 90, 180)
    boundary = (-78.6, -180.0, 90.0, -180.0, 90.0, 180.0, -78.6, 180.0)

    # needed for internal processing
    url = "https://tds.hycom.org/thredds/dodsC/GLBy0.08/expt_93.0/FMRC/GLBy0.08_930_FMRC_best.ncd"
    var_map = {"time": "time",
               "lon": "lon",
               "lat": "lat",
               "z": "depth",
               "u": "water_u",
               "v": "water_v"}
    default_filename = "hycom.nc"

    def __init__(self):
        """ initilize a HYCOM instance"""

        # we may need to query this object before actually
        # opening a OpeNDap session
        # self.open_nc(FileName=self.url)

    @classmethod
    def get_metadata(cls):
        meta_data = super().get_metadata()
        # add anything else here if needed
        # example:
        # note: if want to get the time range, it would be dynamic
        # so this would not be a classmethod, and the object would not
        meta_data["time_range"] = ('2022-01-17T22:00Z', '2022-01-20T22:00Z')
        return meta_data

    def get_data(self,
                 bounds,
                 cross_dateline,
                 max_filesize):
        """
        wrapping this so we can open the opendap connection
        right before querying the data
        """
        self.open_nc(FileName=self.url)
        filepath = super().get_data(bounds, cross_dateline, max_filesize)

        return filepath


