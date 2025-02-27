from .base_models import FVCOM
from libgoods import coops_ofs
from .metadata import Metadata


class COOPS_FVCOM(FVCOM):

    def __init__(self, access='zarr'):

        if access == 'zarr':
            self.access = 'zarr'
            self.location = coops_ofs.get_zarr_url(self)
            
        elif access == 'opendap':
            self.access = 'opendap'
            self.location = coops_ofs.get_ioos_tds_agg_url(self)
            
        elif access == 'local':
            raise NotImplementedError('fixme')
            #this would need start/end time to generate file list

class NGOFS2(COOPS_FVCOM):
    # NOTE: this could all be loaded from a config file (yaml or otherwise, or ...)
    metadata=Metadata(
    identifier="NGOFS2",
    name="NOAA/NOS Northern Gulf of America Operational Forecast System",
    description= "",
    html_desc="""A <a href="http://tidesandcurrents.noaa.gov/ofs/ngofs2/ngofs2.html" target="_blank">
            Northern Gulf of America Operational Forecast System (NGOFS)</a>
            was developed in a joint project of the
            <a href="http://www.nauticalcharts.noaa.gov/" target="_blank">
            NOAA/National Ocean Service's (NOS) Office of Coast Survey </a>,
            the <a href="http://tidesandcurrents.noaa.gov/" target="_blank">
            NOAA/NOS Center for Operational Oceanographic Products and Services (CO-OPS)</a>,
            the <a href="http://mag.ncep.noaa.gov" target="_blank">
            NOAA/National Weather Service's (NWS) National Centers
            for Environmental Prediction (NCEP) Central Operations (NCO)</a>, and the
            <a href="http://fvcom.smast.umassd.edu/" target="_blank">
            University of Massachusetts, Dartmouth </a> using the Finite Volume Coastal Ocean
            Model (FVCOM).
            For detailed model information, visit the NOAA CO-OPS
            <a href="http://tidesandcurrents.noaa.gov/ofs/ngofs2/ngofs_info.html" target="_blank">
            model information page.</a>""",
    regional=True,
    bounding_box=(),
    bounding_poly=(),
    has_depth=True,
    )
    identifier = metadata.identifier   # should this be in both places?
    name = "Northern Gulf of America"
    example_bbox = (-91.5, 29.25, -91, 29.75)
    
class SSCOFS(COOPS_FVCOM):
    
    identifier = 'SSCOFS'
    name = 'Salish Sea and Columbia River'
    example_bbox = (-126.2,47.59,-124.1,49.02)


class LMHOFS(COOPS_FVCOM):
    
    identifier = 'LMHOFS'
    name = 'Lakes Michigan and Huron'
    example_bbox = (-88, 41.57, -86, 44)

class LOOFS(COOPS_FVCOM):
    
    identifier = 'LOOFS'
    name = 'Lake Ontario'
    example_bbox = ()
    
class LSOFS(COOPS_FVCOM):
    
    identifier = 'LSOFS'
    name = 'Lake Superior'
    example_bbox = ()
    
class LEOFS(COOPS_FVCOM):
    
    identifier = 'LEOFS'
    name = 'Lake Erie'
    example_bbox = ()