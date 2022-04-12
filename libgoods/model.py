"""
Base classes for the core data models

Static Model metadata:

{'name': self.name,
 'bounding_box': self.bounding_box, # (lower_left, upper_right)
 'bounds': self.bounds, # thinned polygon ~ 100 points
 'info_text': self.info_text
 'forecast_available': True
 'hindcast_availalbe': False
 'environmental_parameters': ## eg: ['surface winds', 'sea surface temperature']
}

Environmental Parameters will be one of these:
    - This is to make sure we use the same vocabulary everywhere
    - Draft list -- needs much cleaning up.
        surface winds
        surface currents
        3D currents
        sea surface temperature
        ice data
        ...


Dynamic Model Information:

Model.available_times
Model.subset_info(query_params) => info about subset
  - X, Y, Z, T dimensions
  - Estimated File Size
"""

import dataclasses

# FOR NOW, Kristen is putting all standard_names into "environmental paarameters"
# since it's not clear what logic to use to map between the two.
ENVIRONMENTAL_PARAMETERS = {
    "eastward_sea_water_velocity",
    "eastward_wind",
    "northward_sea_water_velocity",
    "northward_wind",
    "ocean_sigma_coordinate",
    "ocean_s_coordinate_g1",
    "ocean_s_coordinate_g2",
    "sea_floor_depth",
    "sea_ice_area_fraction",
    "sea_ice_thickness",
    "sea_surface_height_above_mean_sea_level",
    "sea_water_temperature",
    "sea_water_practical_salinity",
    "time",
    "upward_sea_water_velocity",
}

# # These are the pre-defined environmental parameters
# # this list will need work!
# ENVIRONMENTAL_PARAMETERS = {
#     "surface winds",
#     "surface currents",
#     "3D currents",
#     "sea surface temperature",
#     "ice",
#     "bathymetry",
#     "surface_elevation",
#     "salinity",
# }
#
# # Mapping to connect standard_names associated with each model to
# # the NOAA GOODS environmental parameters
# STANDARD_NAME_MAPPING = {
#     "surface winds": {"eastward_wind", "northward_wind"},
#     "surface currents": {},
#     "3D currents": {"eastward_sea_water_velocity",
#                     "northward_sea_water_velocity",
#                     "upward_sea_water_velocity"},
#     "sea surface temperature": {"sea_water_temperature"},
#     "ice": {"sea_ice_area_fraction", "sea_ice_thickness"},
#     "bathymetry": {"sea_floor_depth"},
#     "surface_elevation": {"sea_surface_height_above_mean_sea_level"},
#     "salinity": {"sea_water_practical_salinity"}
#     }


@dataclasses.dataclass
class Metadata:
    identifier: str = ""
    name: str = ""
    bounding_box: tuple = ()
    bounding_poly: tuple = ()
    info_text: str = ""
    # these need to be thought out more:
    product_type: str = "forecast"  # (forecast or hindcast)
    # KMT: Can we make this generically named?
    start: str = "" # human readable timespan: e.g. "7 days in the past"
    end: str = "" # human readable timespan: e.g. "3 days in the future"

    # # either forecast or hindcast info -- not both
    # forecast_start: str = "" # human readable timespan: e.g. "7 days in the past"
    # forecast_end: str = "" # human readable timespan: e.g. "3 days in the future"
    #
    # hindcast_start: str = ""  # iso datetime string
    # hindcast_end: str = "" # iso datetime string

    environmental_parameters: set = dataclasses.field(default_factory=set)
    """
    class to hold the core meta data for a data source

    This could include validation, or ...

    Currently this has defaults for everything, but maybe it should require everything?
    """

    def __post_init__(self):
        # normalize environmental parameters
        # make sure it's a set:
        self.environmental_parameters = set(self.environmental_parameters)

        # make sure that they are ones we know about
        for ep in self.environmental_parameters:
            if ep not in ENVIRONMENTAL_PARAMETERS:
                raise ValueError(f"{ep} is not a valid environmental parameter")
        # check forecast / hindcast




class Model:
    """
    Base Class for all sources of model results
    """

    # Metadata required by all Data sources
    metadata = Metadata()

    def get_metadata(self):
        """
        Returns a dict of the "static" metadata for this data source
        """
        return dataclasses.asdict(self.metadata)

    def get_model_info(self):
        """
        Returns a dict of both the static and dynamic metadata

        e.g. available times

        -- will there be other info?
          - maybe model meta-data -- when it was run, etc.
          - or is all that in the resulting data files?
        """
        info = self.get_metadata()
        avail = self.get_available_times()
        info["available_times"] = {
            "forecast:": avail["forecast"],
            "hindcast:": avail["hindcast"],
        }
        return info

    def get_available_times(self):
    # def get_available_times(self, cast_type):
        """
        returns the available times for this model as of right now

        This requires reaching out to the source
        """
        raise NotImplementedError

    def get_model_subset_info(
        bounds,
        time_interval,
        environmental_parameters,
        cross_dateline=False,
    ):
        """
        returns info about a subset

        this should also probably cache computations
        needed to determine a subset.

        :returns: dict of (TBA), but maybe:

         {"grid_type":
          "num_grid_cells":
          "num_timesteps":
          "estimated_file_size":
          }
        """

    def get_data(
        self,
        bounds,  # polygon list of (lon, lat) pairs
        time_interval,
        environmental_parameters,
        cross_dateline=False,
        max_filesize=None,
        target_dir=None,
    ):
        """
        The call to actually get the data

        :returns: filepath -- pathlib.Path object of file written
        """
        if not set(environmental_parameters).issubset(
            self.metadata.environmental_parameters
        ):
            raise ValueError(
                f"{environmental_parameters} not supported by this data source"
            )

        # should check for valid time interval here but how / when?
