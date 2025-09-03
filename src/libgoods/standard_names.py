"""
This is a list of the standard names used in libGOODS.
In the model subclasses these are mapped to particular variable names used in the
model output files. The list is included for reference and imported by older classes
in file_processing. The method below returns the standard
names to include based on what "environmental conditions" are being requested -- e.g,
"surface currents" will return the standard names for u/v (surface) velocities.
"""

standard_names = [
    "air_temperature",
    "angle_of_rotation_from_east_to_x",
    "dew_point_temperature",
    "surface_eastward_sea_water_velocity",
    "eastward_sea_water_velocity",
    "eastward_wind",
    "surface_northward_sea_water_velocity",
    "northward_sea_water_velocity",
    "northward_wind",
    "sea_floor_depth",
    "sea_ice_area_fraction",
    "sea_ice_thickness",
    "sea_surface_elevation",
    "sea_water_temperature",
    "sea_water_practical_salinity",
    "upward_sea_water_velocity",
    "wind_gust",
]
"""
The following is a mapping of 'environmental conditions concepts' to the
standard names used in the yaml files. Within the yaml files, these are
in turn mapped to the CF names within the specific model output.
"""
EP_map = {
    "surface winds": ["eastward_wind", "northward_wind"],
    "surface currents": ["surface_eastward_sea_water_velocity", "surface_northward_sea_water_velocity"],
    "3D currents": [
        "eastward_sea_water_velocity",
        "northward_sea_water_velocity",
        #"upward_sea_water_velocity",
    ],
    "surface temperature": ["sea_surface_temperature"],
    "water properties": ["sea_water_temperature", "sea_water_practical_salinity"],
    "ice": [
        "eastward_sea_ice_velocity",
        "northward_sea_ice_velocity",
        "sea_ice_area_fraction",
    ],
}
# WHY is this here twice?

def get_standard_names(env_params):
    """
    Use the mapping specified in EP_map to determine which variables
    to include in the output and return their standard_names.
    Eg, specifying "surface currents" will retrieve output in the
    CF variables mapped to
    "eastward_sea_water_velocity" and "northward_sea_water_velocity"
    """
    EP_map = {
        "surface winds": ["eastward_wind", "northward_wind"],
        "surface currents": ["surface_eastward_sea_water_velocity", "surface_northward_sea_water_velocity"],
        "3D currents": [
            "eastward_sea_water_velocity",
            "northward_sea_water_velocity",
            "upward_sea_water_velocity",
        ],
        "surface temperature": ["sea_surface_temperature"],
        "water properties": ["sea_water_temperature", "sea_water_practical_salinity"],
        "ice": [
            "eastward_sea_ice_velocity",
            "northward_sea_ice_velocity",
            "sea_ice_area_fraction",
        ],
    }

    if isinstance(env_params, list):
        var_list = [var for param in env_params for var in EP_map[param]]
    else:
        var_list = EP_map[env_params]

    return var_list


def get_env_params(standard_names):
    """ """
    params = {k for k, v in EP_map.items() if all(subv in standard_names for subv in v)}

    return params
