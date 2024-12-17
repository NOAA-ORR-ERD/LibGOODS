import libgoods.base_models as bm

tds_url = 'http://pae-paha.pacioos.hawaii.edu/thredds/'


                   
class PacIOOS(bm.ROMS):
    standard_names = bm.ROMS.standard_names.copy()
    tvar = 'time'   
    drop_variables = ['ocean_time','dstart']
    #ocean_time causes problems in output file if included (vars are aggregated on "time") - the dstart is an issue b/c *some* of the files have calendar attribute messed up (gregorian_proleptic instead of proleptic_gregorian) and since we don't need it anyway, we're dropping it
    access = 'opendap'
    standard_names['surface_eastward_sea_water_velocity'] = 'u'
    standard_names['surface_northward_sea_water_velocity'] = 'v'

class HawaiianIslands(PacIOOS):
        long_name = 'Hawaiian Islands 4 km'
        location = tds_url + '/dodsC/hioos/roms_native/hiig/ROMS_Hawaii_Regional_Ocean_Model_Native_Grid_best.ncd'
        
class Oahu(PacIOOS):
        long_name = 'Oahu 1 km'
        location = tds_url + '/dodsC/hioos/roms_native/hiog/ROMS_Oahu_Regional_Ocean_Model_Native_Grid_best.ncd',
        
class OahuSouth(PacIOOS):
        long_name = 'Oahu South Shore'
        location = tds_url + '/dodsC/hioos/roms_native/hiomsg/ROMS_Oahu_South_Shore_Regional_Ocean_Model_Native_Grid_best.ncd'
        
class Waikiki(PacIOOS):
        long_name = 'Waikiki'
        location = tds_url + '/dodsC/hioos/roms_native/hiomsag/ROMS_Waikiki_Regional_Ocean_Model_Native_Grid_best.ncd'
        
class KaneoheBay(PacIOOS):
        long_name = 'Kaneohe Bay'
        location = tds_url + '/dodsC/hioos/roms_native/hioekg/ROMS_Kaneohe_Regional_Ocean_Model_Native_Grid_best.ncd'
        
class PhilippineSea(PacIOOS):
        long_name = 'Philippine Sea'
        location = tds_url +  '/dodsC/pacioos/roms_native/mari/ROMS_CNMI_Regional_Ocean_Model_Native_Grid_best.ncd'       

class GuamNMI(PacIOOS):
        long_name = 'Guam and Northern Mariana Islands'
        location = tds_url +   '/dodsC/pacioos/roms_native/marig/ROMS_Guam_Regional_Ocean_Model_Native_Grid_best.ncd' 
        
class Samoa(PacIOOS):
        long_name = 'Samoa'
        location = tds_url + '/dodsC/pacioos/roms_native/samoa/ROMS_Samoa_Regional_Ocean_Model_Native_Grid_best.ncd'             
