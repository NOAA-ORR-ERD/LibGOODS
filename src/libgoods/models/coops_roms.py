from libgoods import coops_ofs

from . import YAML_DIR
from .base_models import ROMS
from .metadata import Metadata


class COOPS_ROMS(ROMS):
    update_cycle = 6

    def __init__(self, access="zarr", start=None, end=None):
        super().__init__()
        if access == "zarr":
            self.access = "zarr"
            self.location = coops_ofs.get_zarr_url(self.identifier)

        elif access == "opendap":
            self.tvar = "time"
            self.access = "opendap"
            self.location = coops_ofs.get_ioos_tds_agg_url(self.identifier)

        elif access == "local":
            self.access = "local"
            local_dir = "/Volumes/Fury 2/s3"
            self.location = coops_ofs.get_local_flist(
                self.identifier, local_dir, file_type=self.local_file_type, start=start, end=end
            )


class GOMOFS(COOPS_ROMS):
    metadata = Metadata.from_yaml(YAML_DIR / "gomofs.yaml")
    local_file_type = "2ds"


class CIOFS(COOPS_ROMS):
    metadata = Metadata.from_yaml(YAML_DIR / "ciofs.yaml")

    local_file_type = "fields"
    standard_names = ROMS.standard_names.copy()
    standard_names["surface_eastward_sea_water_velocity"] = "u"
    standard_names["surface_northward_sea_water_velocity"] = "v"


class TBOFS(COOPS_ROMS):
    metadata = Metadata.from_yaml(YAML_DIR / "tbofs.yaml")
    local_file_type = "fields"
    standard_names = ROMS.standard_names.copy()
    standard_names["surface_eastward_sea_water_velocity"] = "u"
    standard_names["surface_northward_sea_water_velocity"] = "v"


class DBOFS(COOPS_ROMS):
    metadata = Metadata.from_yaml(YAML_DIR / "dbofs.yaml")

    local_file_type = "fields"
    standard_names = ROMS.standard_names.copy()
    standard_names["surface_eastward_sea_water_velocity"] = "u"
    standard_names["surface_northward_sea_water_velocity"] = "v"


class WCOFS(COOPS_ROMS):
    metadata = Metadata.from_yaml(YAML_DIR / "wcofs.yaml")
    update_cycle = 24
    # name = "West Coast"
    local_file_type = "2ds"


class CBOFS(COOPS_ROMS):
    metadata = Metadata.from_yaml(YAML_DIR / "cbofs.yaml")

    grid_dims = [332, 291, 20]

    local_file_type = "fields"

    standard_names = ROMS.standard_names.copy()
    standard_names["surface_eastward_sea_water_velocity"] = "u"
    standard_names["surface_northward_sea_water_velocity"] = "v"
