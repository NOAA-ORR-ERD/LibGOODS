from .base_xsg import XSGBaseModel
from .metadata import Metadata

base_url = 'https://nomads.ncep.noaa.gov/dods/rtofs/'

# Decent source might be at IOOS EDS
# e.g., http://edsdata.oceansmap.com/thredds/dodsC/EDS/HYCOM_GLOBAL/hycomglobal_20260206.nc
# Individual files by day going back about a month
#  3 hourly with overlap on hour 0 each day
# time goes from 0,3,6,9,12,15,18,21,0 (next day) - trim this last time step when aggregating


class RTOFS(XSGBaseModel):

    metadata = Metadata()
    metadata.identifier = 'RTOFS'
    metadata.name = "NOAA RTOFS"
    chunks = None
    drop_variables = None
    standard_names = {
                      'time': 'time',
                      'longitude': 'lon',
                      'latitude': 'lat',
                      'eastward_sea_water_velocity': 'water_u',
                      'northward_sea_water_velocity': 'water_v',
                      'sea_water_temperature': 'water_temp',
                      'sea_water_practical_salinity': 'salinity',
                      'depth': 'depth',
                      }
    access = "opendap"
    location = None
    is3d = True

    def open_ds():
        pass

    def select_surface(self):
        self.ds = self.ds.isel(height_above_ground2=0)
