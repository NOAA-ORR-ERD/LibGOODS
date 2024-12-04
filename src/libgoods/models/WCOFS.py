import libgoods.base_models as bm
from libgoods import coops_ofs

class WCOFS(bm.roms):

    def __init__(self,source='zarr'):
        super().__init__() 
        
        self.metadata = ''
        
        self.standard_names['surface_eastward_sea_water_velocity'] = 'u'
        self.standard_names['surface_northward_sea_water_velocity'] = 'v'
        self.example_bbox = (-122.0, 25.0, -115.0, 35.0)
        c = coops_ofs.coops('WCOFS')
        
        if source == 'zarr':
            self.tvar = 'ocean_time'
            self.url = c.get_zarr_url()
        elif source == 'ioos_tds':
            self.tvar = 'time'
            self.url = c.get_ioos_tds_agg_url()
        else:
            raise NotImplementedError('Source unknown')

        
