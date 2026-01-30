from . import YAML_DIR
from .base_xsg import GlobalModel
from .metadata import Metadata


class GFS(GlobalModel):

    metadata = Metadata.from_yaml(YAML_DIR / "gfs.yaml")
    chunks = None
    drop_variables = None
    standard_names = {
        "eastward_wind": "u-component_of_wind_height_above_ground",
        "northward_wind": "v-component_of_wind_height_above_ground",
    }
    tvar = "time"
    access = "opendap"
    location = "https://thredds.ucar.edu/thredds/dodsC/grib/NCEP/GFS/Global_0p25deg/Best"

    def open_ds(self):
        # until xarray fix is in -- flip arrays so lat is ascending
        super().open_ds()
        self.ds = self.ds.isel(lat=slice(None, None, -1))
