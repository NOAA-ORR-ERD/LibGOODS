from .base_models import FVCOM
from libgoods import coops_ofs
from .metadata import Metadata
import datetime
from . import YAML_DIR



# the standard names used by the Great Lakes COOPS models
gl_standard_names = FVCOM.standard_names | {"surface_eastward_sea_water_velocity": "u",
                                            "surface_northward_sea_water_velocity": "v",
                                            }

class COOPS_FVCOM(FVCOM):
    update_cycle = 6
    local_file_type = "fields"

    def __init__(self, access="zarr", start=None, end=None):
        super().__init__()

        if access == "zarr":
            self.access = "zarr"
            self.location = coops_ofs.get_zarr_url(self.identifier)

        elif access == "opendap":
            self.access = "opendap"
            self.location = coops_ofs.get_ioos_tds_agg_url(self.identifier)

        elif access == "local":
            self.access = "local"
            local_dir = "/Volumes/Fury 2/s3"
            self.location = coops_ofs.get_local_flist(
                self.identifier, local_dir, file_type=self.local_file_type, start=start, end=end
            )


class NGOFS2(COOPS_FVCOM):
    """
    Code for accessing the NGOFS2 model from coops
    """
    metadata = Metadata.from_yaml(YAML_DIR / "ngofs2.yaml")

    standard_names = FVCOM.standard_names.copy()
    local_file_type = "2ds"  # this is what we're archiving locally


class SSCOFS(COOPS_FVCOM):
    metadata = Metadata.from_yaml(YAML_DIR / 'sscofs.yaml')
    standard_names = gl_standard_names


class LMHOFS(COOPS_FVCOM):
    metadata = Metadata.from_yaml(YAML_DIR / 'lmhofs.yaml')

    standard_names = gl_standard_names



class LOOFS(COOPS_FVCOM):
    metadata = Metadata.from_yaml(YAML_DIR / 'loofs.yaml')

    standard_names = gl_standard_names


class LSOFS(COOPS_FVCOM):
    metadata = Metadata.from_yaml(YAML_DIR / 'lsofs.yaml')

    standard_names = gl_standard_names


class LEOFS(COOPS_FVCOM):
    metadata = Metadata.from_yaml(YAML_DIR / 'leofs.yaml')

    standard_names = gl_standard_names

