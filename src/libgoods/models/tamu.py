from .base_models import ROMS
from .metadata import Metadata
from . import YAML_DIR

# this archive URL may still be good?  https://gcoos5.geos.tamu.edu/thredds/dodsC/NcML/nowcast_agg.nc
# has wind Uwind/Vwind


class TAMU(ROMS):
    metadata = Metadata.from_yaml(YAML_DIR / "tamu.yaml")
    standard_names = ROMS.standard_names.copy()
    standard_names["surface_eastward_sea_water_velocity"] = "u"
    standard_names["surface_northward_sea_water_velocity"] = "v"
    location = "https://gcoos5.geos.tamu.edu/thredds/dodsC/ROFS_latest/txla2_his_f_latest.nc"
    access = "opendap"
    metadata.example_bbox = (-91.5, 29.25, -91, 29.75)
