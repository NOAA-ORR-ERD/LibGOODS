import libgoods.base_models as bm
from libgoods import coops_ofs


class DBOFS(bm.roms):

    def __init__(self):        
        super().__init__()        
        model_info = coops_ofs.OFS_INFO['DBOFS']        
        self.standard_names['surface_eastward_sea_water_velocity'] = 'u'
        self.standard_names['surface_northward_sea_water_velocity'] = 'v'
        self.example_bbox = (-75.5, 38.5, -74.5, 39.25)
        self.access = 'zarr'
        self.location = coops_ofs.get_zarr_url(model_info)


