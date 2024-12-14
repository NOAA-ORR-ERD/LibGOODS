import libgoods.base_models as bm
from libgoods import coops_ofs


class COOPS_ROMS(bm.ROMS):
    
    standard_names = bm.ROMS.standard_names.copy()
    standard_names['surface_eastward_sea_water_velocity'] = 'u'
    standard_names['surface_northward_sea_water_velocity'] = 'v'
    
    update_cycle = 6

    def __init__(self,access='zarr'):  
          
        if access == 'zarr':
            self.access = 'zarr'
            self.location = coops_ofs.get_zarr_url(self)
            
        elif access == 'opendap':
            self.tvar = 'time'
            self.access = 'opendap'
            self.location = coops_ofs.get_ioos_tds_agg_url(self)
            
        elif access == 'local':
            raise NotImplementedError('fixme')
            #this would need start/end time to generate file list

class DBOFS(COOPS_ROMS):
    
    identifier = 'DBOFS'    
    example_bbox = (-75.5, 38.5, -74.5, 39.25)

class WCOFS(COOPS_ROMS):
    
    identifier = 'WCOFS'   
    example_bbox = ()
    update_cycle = 24