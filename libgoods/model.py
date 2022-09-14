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
import shapely.wkt as wkt


# The following is a mapping of 'environmental conditions concepts' to the 'CF concepts' required
# to be present in any given file.
# E.G. In order to state a source can provide 'surface_winds' it must have variables
# with CF standard_name 'eastward_wind' and 'northward_wind' present
ENVIRONMENTAL_PARAMETERS = {
    "surface winds": ["eastward_wind", "northward_wind"],
    "surface currents": ["eastward_sea_water_velocity", "northward_sea_water_velocity"],
    "3D currents": [
        "eastward_sea_water_velocity",
        "northward_sea_water_velocity",
        "upward_sea_water_velocity",
    ],
    "surface temperature": ["sea_surface_temperature"],
    "3D temperature": ["sea_water_temperature"],
    "ice": [
        "eastward_sea_ice_velocity",
        "northward_sea_ice_velocity",
        "sea_ice_area_fraction",
        "eastward_sea_water_velocity",
        "northward_sea_water_velocity",
        "eastward_wind",
        "northward_wind",
    ],
}


@dataclasses.dataclass
class CastMetadata:
    """cast metadata"""

    # metadata for a particular fore/now/hind cast
    # axis: dict = dataclasses.field(default_factory=dict)
    #              'dim_x -> [grid_variable_x]
    period: float = (0,)  # output period in hours
    start: str = ""  # human readable timespan: e.g. "7 days in the past"
    end: str = ""  # human readable timespan
    # dict associating CF name to variable name in data
    # standard_names: dict = dataclasses.field(default_factory=dict)
    env_params: set = dataclasses.field(default_factory=set)

    def init_from_model_cast_metadata(self, metadata):
        # uses a '.(fore/now/hind)cast.metadata dict to populate self
        # self.axis = metadata['axis']
        self.period = metadata.get("output_period_(hr)", 0)
        self.start = metadata["overall_start_datetime"]
        self.end = metadata["overall_end_datetime"]
        # self.standard_names = metadata['standard_names']
        self.env_params = CastMetadata.get_env_params(metadata)
        return self

    @staticmethod
    def get_env_params(metadata):
        """return env parameters"""
        # param metadata: dict of fore/now/hindcast metadata from catalog

        return {
            k
            for k, v in ENVIRONMENTAL_PARAMETERS.items()
            if all([subv in metadata["standard_names"] for subv in v])
        }

    def as_pyson(self):
        """
        returns a JSON compatible dict of the data
        """
        dict_ = dataclasses.asdict(self)
        dict_["env_params"] = list(self.env_params)
        return dict_


@dataclasses.dataclass
class Metadata:
    identifier: str = ""
    name: str = ""
    regional: bool = False
    bounding_box: tuple = ()
    bounding_poly: tuple = ()
    # these need to be thought out more:
    grid_type: str = ""  # 'Regular', 'Curvilinear', 'Unstructured'
    has_depth: bool = True
    dimensions: tuple = ()
    # timestep_interval: float = "" #'1', '0.5', etc
    # either forecast or hindcast info -- not both
    forecast_metadata: CastMetadata = dataclasses.field(default_factory=CastMetadata)
    nowcast_metadata: CastMetadata = dataclasses.field(default_factory=CastMetadata)
    hindcast_metadata: CastMetadata = dataclasses.field(default_factory=CastMetadata)
    env_params: set = dataclasses.field(default_factory=set)
    """
    class to hold the core meta data for a data source

    This could include validation, or ...

    Currently this has defaults for everything, but maybe it should require everything?
    """

    def init_from_model(self, m):
        """initiate a model"""
        # given a model, extract the data and set on self.
        self.identifier = m.name
        self.name = m.description
        self.regional = Metadata.regional_test(m)
        bb = m.metadata["bounding_box"]
        self.bounding_box = bb  # [(a, b) for a, b in zip(bb[::2],bb[1::2])]
        self.bounding_poly = list(
            wkt.loads(m.metadata["geospatial_bounds"]).boundary.coords
        )
        self.grid_type = m.metadata["grid_type"].capitalize()
        grid_dim_keyname = [n for n in m.metadata.keys() if "grid_dim_" in n][0]
        self.has_depth = len(m.metadata[grid_dim_keyname]) == 4
        self.dimensions = m.metadata[grid_dim_keyname]
        # self.timestep_interval = self.get_output_interval(m)
        self.init_cast_metadata(m)
        self.compute_env_params()
        return self

    def init_cast_metadata(self, model):
        """initiate metadata"""
        # given a model, extract the cast start_end times and set them on self
        if hasattr(model, "forecast"):
            self.forecast_metadata.init_from_model_cast_metadata(
                model.forecast.metadata
            )
        if hasattr(model, "hindcast"):
            self.hindcast_metadata.init_from_model_cast_metadata(
                model.hindcast.metadata
            )
        if hasattr(model, "nowcast"):
            self.nowcast_metadata.init_from_model_cast_metadata(model.nowcast.metadata)

    def compute_env_params(self):
        """compute env params"""
        # Computes and sets the list of satisfied environmental parameters
        # An env param is considered satisfied if ALL of fore/now/hindcast can
        # provide that env param.
        self.env_params = (
            self.forecast_metadata.env_params
            & self.nowcast_metadata.env_params
            & self.hindcast_metadata.env_params
        )

    @staticmethod
    def regional_test(model):
        """
        Selection criteria for 'regional' flag in the metadata
        Effectively, a flag to describe what is a 'large' regional model (HYCOM, GFS) and what isnt
        """
        bb = model.metadata["bounding_box"]
        return abs(bb[2] - bb[0]) > 20 or abs(bb[3] - bb[1]) > 20

    def as_pyson(self):
        """
        returns a JSON compatible dict of the data
        """
        dict_ = dataclasses.asdict(self)
        dict_["env_params"] = list(self.env_params)
        dict_["forecast_metadata"] = self.forecast_metadata.as_pyson()
        dict_["hindcast_metadata"] = self.hindcast_metadata.as_pyson()
        dict_["nowcast_metadata"] = self.nowcast_metadata.as_pyson()
        return dict_


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
        return self.metadata.as_pyson()

    def get_model_info(self):
        """
        Returns a dict of both the static and dynamic metadata

        e.g. available times

        -- will there be other info?
          - maybe model meta-data -- when it was run, etc.
          - or is all that in the resulting data files?
        """
        info = self.get_metadata()
        info["available_times"] = {
            "forecast:": self.get_available_times("forecast"),
            "hindcast:": self.get_available_times("hindcast"),
        }

    def get_available_times(self, cast_type):
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

    def get_data_oldcode(
        self,
        desc,
        url,
        bounds,  # polygon list of (lon, lat) pairs
        start,
        end,
        environmental_parameters,
        target_pth,
        ):
        """
        The call to actually get the data

        :returns: filepath -- pathlib.Path object of file written
        """
        if 'ROMS' in desc:
            model = file_processing.roms()
            var_map = {'time':'time'}
        elif 'POM'in desc:
            var_map = {'time':'time','lon':'lon','lat':'lat','u':'u','v':'v'}
            model = file_processing.curv()
        else:
            var_map = {'time':'time','lon':'lon','lat':'lat','u':'water_u','v':'water_v'}
            model = file_processing.rect()
        
        model.open_nc(url)
        #get dimensions to determine subset
        model.get_dimensions(var_map=var_map)
        if model.lon.max() > 180: #should model catalogs tell us the coordinates?
            bounds[0] = bounds[0]+360
            bounds[2] = bounds[2]+360
        
        t1,t2 = model.get_timeslice_indices(start,end)
        #grid subsetting
        model.subset(bounds)
        model.write_nc(var_map=var_map,ofn=target_pth,t_index=[t1,t2,1])
