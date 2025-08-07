from .base import BaseModel
from libgoods.file_processing import rect_model
from .metadata import Metadata
from . import YAML_DIR

class ESPC(BaseModel):
    metadata = Metadata.from_yaml(YAML_DIR / "espc.yaml")
    location = "https://tds.hycom.org/thredds/dodsC/FMRC_ESPC-D-V02_ice/FMRC_ESPC-D-V02_ice_best.ncd"
    access = "opendap"
    chunks = {"time": 1}
    drop_variables = ['tau']
    standard_names = {
        "eastward_sea_water_velocity": "ssu",
        "northward_sea_water_velocity": "ssv",
    }
    tvar = "time"
