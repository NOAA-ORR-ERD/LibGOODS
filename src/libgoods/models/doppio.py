from .base_models import ROMS
from .metadata import Metadata

class DOPPIO(ROMS):
    metadata = Metadata()
    metadata.identifier = 'DOPPIO'
    metadata.name = "Mid-Atlantic Bight and Gulf of Maine (Rutgers)"
    standard_names = ROMS.standard_names.copy()
    standard_names["surface_eastward_sea_water_velocity"] = "u"
    standard_names["surface_northward_sea_water_velocity"] = "v"
    location = "https://tds.marine.rutgers.edu/thredds/dodsC/roms/doppio/2017_da/his/History_Best"
    access = "opendap"

