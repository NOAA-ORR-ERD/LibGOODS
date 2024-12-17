import libgoods.base_models as bm

class BaseNECOFS(bm.FVCOM):
    
    #might not need this base class -- we'll see

    access = 'opendap'

    

class NECOFS(BaseNECOFS):
    long_name = 'Northeast Coastal Ocean Forecast (GOM7)'
    location = 'http://www.smast.umassd.edu:8080/thredds/dodsC/models/fvcom/NECOFS/Forecasts/NECOFS_GOM7_FORECAST.nc'

class MassCoastal(BaseNECOFS):
    long_name = 'Massachusetts Coastal Model'
    location = "http://www.smast.umassd.edu:8080/thredds/dodsC/FVCOM/NECOFS/Forecasts/NECOFS_FVCOM_OCEAN_MASSBAY_FORECAST.nc"

class BostonHarbor(BaseNECOFS):
    long_name = 'Boston Harbor, MA'
    location = "http://www.smast.umassd.edu:8080/thredds/dodsC/FVCOM/NECOFS/Forecasts/NECOFS_FVCOM_OCEAN_BOSTON_FORECAST.nc"

class Hampton(BaseNECOFS):
    long_name = 'Hampton, NH'
    location = "http://www.smast.umassd.edu:8080/thredds/dodsC/FVCOM/NECOFS/Forecasts/NECOFS_FVCOM_OCEAN_HAMPTON_FORECAST.nc"

class Scituate(BaseNECOFS):
    long_name = 'Scituate, MA'
    location = "http://www.smast.umassd.edu:8080/thredds/dodsC/FVCOM/NECOFS/Forecasts/NECOFS_FVCOM_OCEAN_SCITUATE_FORECAST.nc"