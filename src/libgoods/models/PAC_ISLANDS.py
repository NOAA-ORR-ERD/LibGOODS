import libgoods.base_models as bm

tds_url = 'http://pae-paha.pacioos.hawaii.edu/thredds/'

    grids = { 'hiig':'Hawaiian Islands 4 km',
                   'hiog': 'Oahu 1 km',
                   'hiomsg': 'Oahu South Shore',
                   'hiomsag': 'Waikiki',
                   'hioekg': 'Kaneohe Bay',
                   'mari': 'Philippine Sea',
                   'marig': 'Guam and Northern Mariana Islands',
                   'samoa': 'Samoa',}
                   
class base(bm.roms):
                 
    def __init__(self,grid):
        super().__init__() 
        self.tvar = 'time'
        self.standard_names['surface_eastward_sea_water_velocity'] = 'u'
        self.standard_names['surface_northward_sea_water_velocity'] = 'v'

class hiig(base):
        super().__init__()
        self.name = 'Hawaiian Islands 4 km',
        self.url = tds_url + '/dodsC/hioos/roms_native/hiig/ROMS_Hawaii_Regional_Ocean_Model_Native_Grid_best.ncd'
   
class hiog(base):
        super().__init__()
        self.name = 'Oahu 1 km',
        self.url = tds_url + '/dodsC/hioos/roms_native/hiog/ROMS_Oahu_Regional_Ocean_Model_Native_Grid_best.ncd''
        
class hiomsg(base):
        super().__init__()
        self.name = 'Oahu South Shore',
        self.url = tds_url + '/dodsC/hioos/roms_native/hiomsg/ROMS_Oahu_South_Shore_Regional_Ocean_Model_Native_Grid_best.ncd'

class hiomsag(base):
        super().__init__()
        self.name = 'Waikiki',
        self.url = tds_url + '/dodsC/hioos/roms_native/hiomsag/ROMS_Waikiki_Regional_Ocean_Model_Native_Grid_best.ncd'

class hioekg(base):
        super().__init__()
        self.name = 'Kaneohe Bay',
        self.url = tds_url + '/dodsC/hioos/roms_native/hioekg/ROMS_Kaneohe_Regional_Ocean_Model_Native_Grid_best.ncd'

class mari(base):
        super().__init__()
        self.name = 'Philippine Sea',
        self.url = tds_url + '/dodsC/pacioos/roms_native/mari/ROMS_CNMI_Regional_Ocean_Model_Native_Grid_best.ncd'

class marig(base):
        super().__init__()
        self.name = 'Guam and Northern Mariana Islands',
        self.url = tds_url + '/dodsC/pacioos/roms_native/marig/ROMS_Guam_Regional_Ocean_Model_Native_Grid_best.ncd'

class samoa(base):
        super().__init__()
        self.name = 'Samoa',
        self.url = tds_url + '/dodsC/pacioos/roms_native/samoa/ROMS_Samoa_Regional_Ocean_Model_Native_Grid_best.ncd'        