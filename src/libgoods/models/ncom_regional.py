from .base_models import BaseModel

tds_url = 'http://pae-paha.pacioos.hawaii.edu/thredds/'


class NCOM(BaseModel):

    chunks = None
    tvar = 'time'
    drop_variables = None
    access = 'opendap'
    standard_names = {}
    standard_names['surface_eastward_sea_water_velocity'] = 'water_u'
    standard_names['surface_northward_sea_water_velocity'] = 'water_v'


class AmSeas(NCOM):

    name = "American Seas NCOM 3 km"
    location = "https://www.ncei.noaa.gov/thredds-coastal/dodsC/ncom_amseas_agg/AmSeas_Dec_17_2020_to_Current_best.ncd"
    desc = """
            The Naval Oceanographic Office operational ocean prediction system for the 
            Gulf of Mexico and Caribbean is a ~3km resolution model based on the 
            Navy Coastal Ocean Model. 
            """

class USEast(NCOM):

    name = "https://www.ncei.noaa.gov/thredds-coastal/dodsC/ncom_us_east_agg/US_East_Dec_17_2020_to_Current_best.ncd"
    location = "https://www.ncei.noaa.gov/thredds-coastal/dodsC/ncom_amseas_agg/AmSeas_Dec_17_2020_to_Current_best.ncd"
    desc = """
            The Naval Oceanographic Office operational ocean prediction system 
            for waters off the east coast of the U.S. is a ~3km resolution 
            model based on the Navy Coastal Ocean Model.
            """

class Alaska(NCOM):

    name = "American Seas NCOM 3 km"
    location = "https://www.ncei.noaa.gov/thredds-coastal/dodsC/ncom_alaska_agg/Alaska_Dec_17_2020_to_Current_best.ncd"
    desc = """
            The Naval Oceanographic Office operational ocean prediction system 
            for waters of the NE Pacific including the Gulf fo Alaska
            is a ~3km resolution 
            model based on the Navy Coastal Ocean Model.
            """