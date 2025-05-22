from .base_models import ROMS
from libgoods import coops_ofs


class COOPS_ROMS(ROMS):
    update_cycle = 6

    def __init__(self, access="zarr", start=None, end=None):
        if access == "zarr":
            self.access = "zarr"
            self.location = coops_ofs.get_zarr_url(self)

        elif access == "opendap":
            self.tvar = "time"
            self.access = "opendap"
            self.location = coops_ofs.get_ioos_tds_agg_url(self)

        elif access == "local":
            self.access = "local"
            local_dir = "/Volumes/Fury 2/s3"
            self.location = coops_ofs.get_local_flist(
                self, local_dir, file_type=self.local_file_type, start=start, end=end
            )


class GOMOFS(COOPS_ROMS):
    # identifier = "GOMOFS"
    example_bbox = ()
    # name = "Gulf of Maine"
    local_file_type = "2ds"


class CIOFS(COOPS_ROMS):
    # identifier = "CIOFS"
    example_bbox = ()
    # name = "Cook Inlet"
    local_file_type = "fields"
    standard_names = ROMS.standard_names.copy()
    standard_names["surface_eastward_sea_water_velocity"] = "u"
    standard_names["surface_northward_sea_water_velocity"] = "v"


class TBOFS(COOPS_ROMS):
    # identifier = "TBOFS"
    example_bbox = ()
    # name = "Tampa Bay"
    local_file_type = "fields"
    standard_names = ROMS.standard_names.copy()
    standard_names["surface_eastward_sea_water_velocity"] = "u"
    standard_names["surface_northward_sea_water_velocity"] = "v"


class DBOFS(COOPS_ROMS):
    # identifier = "DBOFS"
    example_bbox = (-75.5, 38.5, -74.5, 39.25)
    # name = "Delaware Bay"
    local_file_type = "fields"
    standard_names = ROMS.standard_names.copy()
    standard_names["surface_eastward_sea_water_velocity"] = "u"
    standard_names["surface_northward_sea_water_velocity"] = "v"


class WCOFS(COOPS_ROMS):
    # identifier = "WCOFS"
    example_bbox = (-122.0, 25.0, -115.0, 35.0)
    update_cycle = 24
    # name = "West Coast"
    local_file_type = "2ds"


class CBOFS(COOPS_ROMS):
    # identifier = "CBOFS"
    example_bbox = (-76.5, 36.75, -75.25, 37.75)
    grid_dims = [332, 291, 20]
    # name = "Chesapeake Bay"
    local_file_type = "fields"
    # html_desc = r'The <a href="http://tidesandcurrents.noaa.gov/ofs/cbofs/cbofs.html" target="_blank"> Chesapeake Bay Operational Forecast System (CBOFS)</a> was developed by the <a href="http://www.nauticalcharts.noaa.gov/" target="_blank">NOAA/National Ocean Service/Office of Coast Survey</a> in a joint project with the <a href="http://tidesandcurrents.noaa.gov/" target="_blank"> NOAA/NOS/Center for Operational Oceanographic Products and Services(CO-OPS)</a> and the <a href="http://mag.ncep.noaa.gov" target="_blank">NOAA/National Weather Service/National Centers for Environmental Prediction (NCEP) Central Operations (NCO)</a> using the Regional Ocean Modeling System (ROMS)</a>. For detailed model information, visit the NOAA CO-OPS <a href="http://tidesandcurrents.noaa.gov/ofs/cbofs/cbofs_info.html" target="_blank">model information page.</a>'
    standard_names = ROMS.standard_names.copy()
    standard_names["surface_eastward_sea_water_velocity"] = "u"
    standard_names["surface_northward_sea_water_velocity"] = "v"
