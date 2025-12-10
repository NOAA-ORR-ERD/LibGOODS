
from libgoods import coops_ofs

from . import YAML_DIR
from .base_xsg import ROMS
from .metadata import Metadata


class COOPS_ROMS(ROMS):
    update_cycle = 6

    def __init__(self, access="zarr", start=None, end=None, archive_dir=None):
        # start/end are only used for local archives to create file list
        super().__init__()
        self.is3d = True
        if access == "zarr":
            self.access = "zarr"
            self.location = coops_ofs.get_zarr_url(self.identifier)
            self.metadata.start = 'approximately one week before present time'
            self.metadata.end = 'the 48-120 hours forecast period'

        elif access == "opendap":
            self.tvar = "time"
            self.access = "opendap"
            self.location = coops_ofs.get_ioos_tds_agg_url(self.identifier)

        elif access == "local":
            self.access = "local"
            # local_dir = "/Volumes/Fury 2/s3"

            self.location = coops_ofs.get_local_flist(
                self.identifier, archive_dir, file_type=self.local_file_type, start=start, end=end
            )
            self.actual_start = coops_ofs.file2dt(self.location[0], self.update_cycle)
            self.actual_end = coops_ofs.file2dt(self.location[-1], self.update_cycle)
            if self.local_file_type == '2ds':
                self.is3d = False
                self.standard_names = (ROMS.standard_names
                                       | {"eastward_sea_water_velocity": "u_sur",
                                          "northward_sea_water_velocity": "v_sur",
                                          "sea_water_temperature": "temp_sur",
                                          "sea_water_practical_salinity": "salt_sur"
                                          })


class GOMOFS(COOPS_ROMS):
    metadata = Metadata.from_yaml(YAML_DIR / "gomofs.yaml")
    local_file_type = "2ds"


class CIOFS(COOPS_ROMS):
    metadata = Metadata.from_yaml(YAML_DIR / "ciofs.yaml")
    local_file_type = "fields"

class TBOFS(COOPS_ROMS):
    metadata = Metadata.from_yaml(YAML_DIR / "tbofs.yaml")
    local_file_type = "fields"

class DBOFS(COOPS_ROMS):
    metadata = Metadata.from_yaml(YAML_DIR / "dbofs.yaml")
    local_file_type = "fields"

class WCOFS(COOPS_ROMS):
    metadata = Metadata.from_yaml(YAML_DIR / "wcofs.yaml")
    update_cycle = 24
    local_file_type = "2ds"

class CBOFS(COOPS_ROMS):
    metadata = Metadata.from_yaml(YAML_DIR / "cbofs.yaml")
    local_file_type = "fields"
