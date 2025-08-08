from .base_nc4 import NC4BaseModel

from .metadata import Metadata
from . import YAML_DIR

class ESPC(NC4BaseModel):
    metadata = Metadata.from_yaml(YAML_DIR / "espc.yaml")
    location = "https://tds.hycom.org/thredds/dodsC/FMRC_ESPC-D-V02_ice/FMRC_ESPC-D-V02_ice_best.ncd"

    #tvar = "time"
    standard_names = {'time': 'time',
                      'longitude': 'lon',
                      'latitude': 'lat',
                      'eastward_sea_water_velocity': 'ssu',
                      'northward_sea_water_velocity': 'ssv'}