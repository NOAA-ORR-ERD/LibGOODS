import libgoods.base_models as bm

tds_url = 'http://pae-paha.pacioos.hawaii.edu/thredds/'

grids = {'hiig':'Hawaiian Islands 4 km',
         'hiog': 'Oahu 1 km',
         'hiomsg': 'Oahu South Shore',
         'hiomsag': 'Waikiki',
         'hioekg': 'Kaneohe Bay',
         'mari': 'Philippine Sea',
         'marig': 'Guam and Northern Mariana Islands',
         'samoa': 'Samoa'}
         
urls = {'hiig': '/dodsC/hioos/roms_native/hiig/ROMS_Hawaii_Regional_Ocean_Model_Native_Grid_best.ncd',
        'hiog': '/dodsC/hioos/roms_native/hiog/ROMS_Oahu_Regional_Ocean_Model_Native_Grid_best.ncd',
        'hiomsg': '/dodsC/hioos/roms_native/hiomsg/ROMS_Oahu_South_Shore_Regional_Ocean_Model_Native_Grid_best.ncd',
        'hiomsag': '/dodsC/hioos/roms_native/hiomsag/ROMS_Waikiki_Regional_Ocean_Model_Native_Grid_best.ncd',
        'hioekg': '/dodsC/hioos/roms_native/hioekg/ROMS_Kaneohe_Regional_Ocean_Model_Native_Grid_best.ncd',
        'mari': '/dodsC/pacioos/roms_native/mari/ROMS_CNMI_Regional_Ocean_Model_Native_Grid_best.ncd',
        'marig': '/dodsC/pacioos/roms_native/marig/ROMS_Guam_Regional_Ocean_Model_Native_Grid_best.ncd',
        'samoa': '/dodsC/pacioos/roms_native/samoa/ROMS_Samoa_Regional_Ocean_Model_Native_Grid_best.ncd'}
                   
class base(bm.roms):
                 
    def __init__(self,grid):
        super().__init__() 
        self.tvar = 'time'
        self.drop_variables = 'ocean_time'
        self.name = grids[grid]
        self.location = tds_url + urls[grid]
        self.access = 'opendap'
        self.standard_names['surface_eastward_sea_water_velocity'] = 'u'
        self.standard_names['surface_northward_sea_water_velocity'] = 'v'


   
