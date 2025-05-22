from .base_models import BaseModel


class NCOM(BaseModel):
    model = "ncom"
    chunks = None
    drop_variables = None
    standard_names = {
        "eastward_sea_water_velocity": "water_u",
        "northward_sea_water_velocity": "water_v",
        "upward_sea_water_velocity": "water_w",
        "sea_surface_elevation": "surf_el",
        "sea_water_temperature": "water_temp",
        "sea_water_practical_salinity": "salinity",
    }
    tvar = "time"
    zcoord = "depth"
    access = "opendap"
    location = None

    def filter_variables(self, variable_list=None, is3d=False):
        # variable list default is based on surface u/v variable names
        if variable_list is None:
            variable_list = ["eastward_sea_water_velocity", "northward_sea_water_velocity"]

        vars2include = [self.standard_names[v] for v in variable_list]

        self.ds = self.ds.xsg.subset_vars(vars2include)

    def select_surface(self):
        self.ds = self.ds.isel(depth=0)


class AmSeas(NCOM):
    name = "American Seas NCOM 3 km"
    location = "https://www.ncei.noaa.gov/thredds-coastal/dodsC/ncom_amseas_agg/AmSeas_Dec_17_2020_to_Current_best.ncd"
    desc = """
            The Naval Oceanographic Office operational ocean prediction system for the 
            Gulf of Mexico and Caribbean is a ~3km resolution model based on the 
            Navy Coastal Ocean Model. 
            """
    example_bbox = (-91.5 + 360, 29.25, -91 + 360, 29.75)


class USEast(NCOM):
    name = "US East NCOM 3 km"
    location = "https://www.ncei.noaa.gov/thredds-coastal/dodsC/ncom_amseas_agg/AmSeas_Dec_17_2020_to_Current_best.ncd"
    desc = """
            The Naval Oceanographic Office operational ocean prediction system 
            for waters off the east coast of the U.S. is a ~3km resolution 
            model based on the Navy Coastal Ocean Model.
            """


class Alaska(NCOM):
    name = "Gulf of Alaska NCOM 3 km"
    location = "https://www.ncei.noaa.gov/thredds-coastal/dodsC/ncom_alaska_agg/Alaska_Dec_17_2020_to_Current_best.ncd"
    desc = """
            The Naval Oceanographic Office operational ocean prediction system 
            for waters of the NE Pacific including the Gulf fo Alaska
            is a ~3km resolution 
            model based on the Navy Coastal Ocean Model.
            """
