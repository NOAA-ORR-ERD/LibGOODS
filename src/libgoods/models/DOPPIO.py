import libgoods.base_models as bm

class DOPPIO(bm.roms):

    def __init__(self):
        super().__init__() 
        self.url = 'https://tds.marine.rutgers.edu/thredds/dodsC/roms/doppio/2017_da/his/History_Best'
        self.name = 'ROMS based circulation model for the Mid-Atlantic Bight and Gulf of Maine developed at the Institute for Marine and Coastal Sciences, Rutgers University'
        self.tvar = 'time'
        self.standard_names['surface_eastward_sea_water_velocity'] = 'u'
        self.standard_names['surface_northward_sea_water_velocity'] = 'v'

        
