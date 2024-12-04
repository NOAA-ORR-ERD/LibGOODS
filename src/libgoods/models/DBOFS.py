import libgoods.base_models as bm
from libgoods import coops_ofs

class DBOFS(bm.roms):

    def __init__(self,source='zarr'):
        super().__init__() 
        
        self.metadata = ''
        self.tvar = 'ocean_time'
        self.standard_names['surface_eastward_sea_water_velocity'] = 'u'
        self.standard_names['surface_northward_sea_water_velocity'] = 'v'
        self.example_bbox = (-75.5, 38.5, -74.5, 39.25)
        c = coops_ofs.coops('DBOFS')
        
        if source == 'zarr':
            self.url = c.get_zarr_url()

        
