"""
HYCOM global ocean model
"""
import os
from ..data_models import Currents
from .. import rect_model, roms_model, temp_files_dir, currents_dir
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

class HYCOM(Currents):
    """
    global HYCOM
    """
    # Much of this could be loaded from JSON, or?
    # not sure if that would make it easier?
    name = "Global Ocean Forecasting System (GOFS) 3.1"
    url = "https://tds.hycom.org/thredds/dodsC/GLBy0.08/expt_93.0/FMRC/GLBy0.08_930_FMRC_best.ncd"
    info_text = INFO_TEXT
    bounding_box = (-78.6, -180, 90, 180)
    boundary = (-78.6, -180.0, 90.0, -180.0, 90.0, 180.0, -78.6, 180.0)
    var_map = {"time": "time",
               "lon": "lon",
               "lat": "lat",
               "z": "depth",
               "u": "water_u",
               "v": "water_v"}
    grid_type = "rect"
    default_filename = "hycom.nc"

    def __init__(self):
        """ initilize a HYCOM instance"""
        # nothing to do here
        # but maybe in the future:
        # ping to see if teh server is running?
        # check if anything's chagned? bounding box, etc.

        # other configuration?
        pass

    def get_data(self,
                 bounds,
                 cross_dateline,
                 max_filesize):

            '''
            :param: bounds Sequence of (lon,lat) pairs e.g., [(lon,lat),(lon,lat)...] 
            
            '''
            try:
                bounding_box = polygon2bbox(bounds)
            except ValueError:
                raise NotImplementedError('Only rectangular bounds are supported')
                
            #bounds = [south_lat,west_lon,north_lat,east_lon]
            url = self.url
            var_map = self.var_map

            model = rect_model.rect(url)

            model.get_dimensions(var_map)
            
            model.subset(bounding_box)

            #until I add time selection -- return last 10 time steps
            tlen = len(model.time)

            fn = self.default_filename
            fp = os.path.join(temp_files_dir,fn)
            model.write_nc(var_map,fp,t_index=[tlen-10,tlen,1])

            return fn, fp
