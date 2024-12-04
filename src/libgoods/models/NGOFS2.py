import libgoods.base_models as bm
from libgoods import coops_ofs

class NGOFS2(bm.fvcom):

    def __init__(self,source='zarr'):
        super().__init__() 
        
        self.name = 'NOAA/NOS Northern Gulf of Mexico Operational Forecast System'
        self.example_bbox = (-91.5, 29.25, -91, 29.75)
        c = coops_ofs.coops('NGOFS2')
        
        if source == 'zarr':
            self.url = c.get_zarr_url()

        
