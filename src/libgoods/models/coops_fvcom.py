

from libgoods import coops_ofs

from . import YAML_DIR
from .base_xsg import FVCOM
from .metadata import Metadata


class COOPS_FVCOM(FVCOM):
    update_cycle = 6

    def __init__(self, access="zarr", start=None, end=None, archive_dir=None):
        # start/end are only used for local archives to create file list

        if access == "zarr":
            super().__init__()
            self.access = "zarr"
            self.location = coops_ofs.get_zarr_url(self.identifier)

        elif access == "opendap":
            super().__init__()
            self.access = "opendap"
            self.location = coops_ofs.get_ioos_tds_agg_url(self.identifier)

        elif access == "local":

            if self.local_file_type == '2ds':
                super().__init__(is3d=False)
                self.standard_names = (FVCOM.standard_names
                                       | {"eastward_sea_water_velocity": "u_surface",
                                           "northward_sea_water_velocity": "v_surface",
                                           "sea_water_temperature": "temp_surface",
                                           "sea_water_practical_salinity": "salt_surface"
                                          })
            else:
                super().__init__()
            self.concat_dim = 'time'
            self.access = 'local'
            self.location = coops_ofs.get_local_flist(
                    self.identifier, archive_dir,
                    file_type=self.local_file_type,
                    start=start,
                    end=end
                )
            self.actual_start = coops_ofs.file2dt(self.location[0], self.update_cycle)
            self.actual_end = coops_ofs.file2dt(self.location[-1], self.update_cycle)


class NGOFS2(COOPS_FVCOM):
    """
    Code for accessing the NGOFS2 model from coops
    """
    metadata = Metadata.from_yaml(YAML_DIR / "ngofs2.yaml")
    local_file_type = "2ds"  # this is what we're archiving locally


class SSCOFS(COOPS_FVCOM):
    metadata = Metadata.from_yaml(YAML_DIR / 'sscofs.yaml')
    local_file_type = "fields"


class LMHOFS(COOPS_FVCOM):
    metadata = Metadata.from_yaml(YAML_DIR / 'lmhofs.yaml')
    local_file_type = "fields"


class LOOFS(COOPS_FVCOM):
    metadata = Metadata.from_yaml(YAML_DIR / 'loofs.yaml')
    local_file_type = "fields"


class LSOFS(COOPS_FVCOM):
    metadata = Metadata.from_yaml(YAML_DIR / 'lsofs.yaml')
    local_file_type = "fields"


class LEOFS(COOPS_FVCOM):
    metadata = Metadata.from_yaml(YAML_DIR / 'leofs.yaml')
    local_file_type = "fields"
