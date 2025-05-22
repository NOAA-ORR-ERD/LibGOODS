from .base_models import FVCOM
from libgoods import coops_ofs
from .metadata import Metadata
import datetime

class COOPS_FVCOM(FVCOM):

    update_cycle = 6

    def __init__(self, access='zarr', start=None, end=None):

        if access == 'zarr':
            self.access = 'zarr'
            self.location = coops_ofs.get_zarr_url(self)
            
        elif access == 'opendap':
            self.access = 'opendap'
            self.location = coops_ofs.get_ioos_tds_agg_url(self)
            
        elif access == 'local':
            self.access = 'local'
            local_dir = '/Volumes/Fury 2/s3'
            self.location = coops_ofs.get_local_flist(self, local_dir, file_type=self.local_file_type, 
                                                      start=start, end=end)

class NGOFS2(COOPS_FVCOM):

    yaml_filename = 'ngofs2.yaml'

    # metadata=Metadata(
    #     identifier="NGOFS2",
    #     name="NOAA/NOS Northern Gulf of America Operational Forecast System",
    #     description="",
    #     html_desc="""A <a href="http://tidesandcurrents.noaa.gov/ofs/ngofs2/ngofs2.html" target="_blank">
    #         Northern Gulf of America Operational Forecast System (NGOFS)</a>
    #         was developed in a joint project of the
    #         <a href="http://www.nauticalcharts.noaa.gov/" target="_blank">
    #         NOAA/National Ocean Service's (NOS) Office of Coast Survey </a>,
    #         the <a href="http://tidesandcurrents.noaa.gov/" target="_blank">
    #         NOAA/NOS Center for Operational Oceanographic Products and Services (CO-OPS)</a>,
    #         the <a href="http://mag.ncep.noaa.gov" target="_blank">
    #         NOAA/National Weather Service's (NWS) National Centers
    #         for Environmental Prediction (NCEP) Central Operations (NCO)</a>, and the
    #         <a href="http://fvcom.smast.umassd.edu/" target="_blank">
    #         University of Massachusetts, Dartmouth </a> using the Finite Volume Coastal Ocean
    #         Model (FVCOM).
    #         For detailed model information, visit the NOAA CO-OPS
    #         <a href="http://tidesandcurrents.noaa.gov/ofs/ngofs2/ngofs_info.html" target="_blank">
    #         model information page.</a>""",
    #     regional=True,
    #     bounding_box=(),
    #     bounding_poly=(),
    # )
    # name = "Northern Gulf of America"
    example_bbox = (-91.5, 29.25, -91, 29.75)
    local_file_type = '2ds'  # this is what we're archiving locally

class SSCOFS(COOPS_FVCOM):
    
    metadata=Metadata(
        identifier = 'SSCOFS',
        name = 'Salish Sea and Columbia River',
        example_bbox = (-126.2,47.59,-124.1,49.02),
        local_file_type = 'fields', 
    )

    standard_names = FVCOM.standard_names.copy()
    standard_names['surface_eastward_sea_water_velocity'] = 'u'
    standard_names['surface_northward_sea_water_velocity'] = 'v'

class LMHOFS(COOPS_FVCOM):


    local_file_type = 'fields'
    standard_names = FVCOM.standard_names.copy()
    standard_names['surface_eastward_sea_water_velocity'] = 'u'
    standard_names['surface_northward_sea_water_velocity'] = 'v'

class LOOFS(COOPS_FVCOM):
    
    identifier = 'LOOFS'
    name = 'Lake Ontario'
    example_bbox = ()
    local_file_type = 'fields'
    standard_names = FVCOM.standard_names.copy()
    standard_names['surface_eastward_sea_water_velocity'] = 'u'
    standard_names['surface_northward_sea_water_velocity'] = 'v'
    
class LSOFS(COOPS_FVCOM):
    
    identifier = 'LSOFS'
    name = 'Lake Superior'
    example_bbox = ()
    local_file_type = 'fields'
    standard_names = FVCOM.standard_names.copy()
    standard_names['surface_eastward_sea_water_velocity'] = 'u'
    standard_names['surface_northward_sea_water_velocity'] = 'v'
    
class LEOFS(COOPS_FVCOM):
    
    identifier = 'LEOFS'
    name = 'Lake Erie'
    example_bbox = ()
    local_file_type = 'fields'
    standard_names = FVCOM.standard_names.copy()
    standard_names['surface_eastward_sea_water_velocity'] = 'u'
    standard_names['surface_northward_sea_water_velocity'] = 'v'
