from . import YAML_DIR
#from .base_nc4 import NC4BaseModel as BaseModel
from .base_xsg import GlobalModel as BaseModel
from .metadata import Metadata


class ESPC(BaseModel):
    access = "opendap"
    metadata = Metadata.from_yaml(YAML_DIR / "espc.yaml")
    location = "https://tds.hycom.org/thredds/dodsC/FMRC_ESPC-D-V02_all/FMRC_ESPC-D-V02_all_best.ncd"
    is3d = True
    drop_variables = ['tau'] #needed by xarray only
    chunks = None
    standard_names = { #this has dims also to be compatible with old code
                      'time': 'time',
                      'longitude': 'lon',
                      'latitude': 'lat',
                      'eastward_sea_water_velocity': 'water_u',
                      'surface_eastward_sea_water_velocity': 'water_u',
                      'northward_sea_water_velocity': 'water_v',
                      'surface_northward_sea_water_velocity': 'water_v',
                      'sea_water_temperature': 'water_temp',
                      'sea_water_practical_salinity': 'salinity',
                      'depth': 'depth',
                      }
    tvar = "time"
