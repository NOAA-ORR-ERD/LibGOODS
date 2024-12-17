import libgoods.base_models as bm

class DOPPIO(bm.ROMS):
    
    standard_names = bm.ROMS.standard_names.copy()
    standard_names['surface_eastward_sea_water_velocity'] = 'u'    
    standard_names['surface_northward_sea_water_velocity'] = 'v'
    location = 'https://tds.marine.rutgers.edu/thredds/dodsC/roms/doppio/2017_da/his/History_Best'
    access = 'opendap'
    long_name = 'ROMS based circulation model for the Mid-Atlantic Bight and Gulf of Maine developed at the Institute for Marine and Coastal Sciences, Rutgers University'
    



