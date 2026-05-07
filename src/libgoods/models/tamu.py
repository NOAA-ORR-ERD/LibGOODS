from . import YAML_DIR
from .base_xsg import ROMS
from .metadata import Metadata

# this archive URL may still be good?  https://gcoos5.geos.tamu.edu/thredds/dodsC/NcML/nowcast_agg.nc
# has wind Uwind/Vwind


class TAMU(ROMS):
    metadata = Metadata.from_yaml(YAML_DIR / "tamu.yaml")
    standard_names = ROMS.standard_names.copy()
    location = "https://gcoos5.geos.tamu.edu/thredds/dodsC/ROFS_latest/txla2_his_f_latest.nc"
    access = "opendap"

