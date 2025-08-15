from .base_nc4 import NC4BaseModel

from .metadata import Metadata
from . import YAML_DIR


class ESPC(NC4BaseModel):
    metadata = Metadata.from_yaml(YAML_DIR / "espc.yaml")
    location = "https://tds.hycom.org/thredds/dodsC/FMRC_ESPC-D-V02_all/FMRC_ESPC-D-V02_all_best.ncd"

    standard_names = {
                      'time': 'time',
                      'longitude': 'lon',
                      'latitude': 'lat',
                      'eastward_sea_water_velocity': 'water_u',
                      'northward_sea_water_velocity': 'water_v',
                      'sea_water_temperature': 'water_temp',
                      'sea_water_practical_salinity': 'salinity',
                      }
