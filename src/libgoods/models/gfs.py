from . import YAML_DIR
from .base_xsg import XSGBaseModel
from .metadata import Metadata


class GFS(XSGBaseModel):

    metadata = Metadata.from_yaml(YAML_DIR / "gfs.yaml")
    chunks = None
    drop_variables = None
    standard_names = {
        "eastward_wind": "u-component_of_wind_height_above_ground",
        "northward_wind": "v-component_of_wind_height_above_ground",
    }
    access = "opendap"
    location = "https://thredds.ucar.edu/thredds/dodsC/grib/NCEP/GFS/Global_0p25deg/Best"

    def select_surface(self):
        # subset_vertical_level uses sel based on vertical coord
        # here its height_above_ground = 10
        self.ds = self.ds.xsg.subset_vertical_level(level=10, method='nearest')
