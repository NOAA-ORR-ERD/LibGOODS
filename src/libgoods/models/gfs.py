from .base_xsg import XSGBaseModel
from .metadata import Metadata


class GFS(XSGBaseModel):

    metadata = Metadata()
    metadata.identifier = 'GFS'
    metadata.name = "Global Forecast System 0.25 degrees"
    chunks = None
    drop_variables = None
    standard_names = {
        "eastward_wind": "u-component_of_wind_height_above_ground",
        "northward_wind": "v-component_of_wind_height_above_ground",
    }
    tvar = "time"
    access = "opendap"
    location = "http://eds.ioos.us/thredds/dodsC/ioos/gfs/0p25/Best"




