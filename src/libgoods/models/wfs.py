import libgoods.base_models as bm

class BaseWFS(bm.FVCOM):
    
    #might not need this base class -- we'll see

    access = 'opendap'

    

class WFCOM(BaseWFS):
    long_name = 'West Florida Coastal Ocean Circulation Model (WFCOM)'
    location = 'http://ocgtds.marine.usf.edu:8080/thredds/dodsC/WFCOM4_NF_model/WFCOM4_NF_20250210.nc'


class TBCOM(BaseWFS):
    long_name = 'West Florida Coastal Ocean Circulation Model (WFCOM)'
    location = 'http://ocgtds.marine.usf.edu:8080/thredds/dodsC/TBCOM2_NF_model/TBCOM2_NF_20250211.nc'