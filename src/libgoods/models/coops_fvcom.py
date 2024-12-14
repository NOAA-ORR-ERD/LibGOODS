import libgoods.base_models as bm
from libgoods import coops_ofs


class COOPS_FVCOM(bm.FVCOM):

    def __init__(self,access='zarr'):

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
    
    identifier = 'NGOFS2'
    name = 'NOAA/NOS Northern Gulf of Mexico Operational Forecast System'
    example_bbox = (-91.5, 29.25, -91, 29.75)