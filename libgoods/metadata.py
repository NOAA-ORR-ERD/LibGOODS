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

"""
The following is a mapping of 'environmental conditions concepts' to the standard names 
used in the model_catalogs package. These are in turn mapped to the CF names within the 
specific model output. Thus specifying "surface currents" will retrieve output in the 
CF variables mapped to "eastward_sea_water_velocity" and "northward_sea_water_velocity"
"""
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
class SourceMetadata:
    """source metadata"""

    # metadata for a particular model source
    # axis: dict = dataclasses.field(default_factory=dict)
    #              'dim_x -> [grid_variable_x]
    name: str = ""
    period: float = (0,)  # output period in hours
    start: str = ""  # human readable timespan: e.g. "7 days in the past"
    end: str = ""  # human readable timespan
    # dict associating CF name to variable name in data
    standard_names: dict = dataclasses.field(default_factory=dict)
    env_params: set = dataclasses.field(default_factory=set)

    def init_from_model_source(self, src):
        # uses a '.(fore/now/hind)cast.metadata dict to populate self
        # self.axis = metadata['axis']
        self.name = src.name
        self.period = src.metadata.get("output_period_(hr)", 0)
        self.start = src.metadata["overall_start_datetime"]
        self.end = src.metadata["overall_end_datetime"]
        self.standard_names = src.metadata["standard_names"]
        # self.standard_names = metadata['standard_names']
        self.env_params = SourceMetadata.get_env_params(src.metadata)
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
    description: str = ""
    html_desc: str = ""
    regional: bool = False
    bounding_box: tuple = ()
    bounding_poly: tuple = ()
    # these need to be thought out more:
    grid_type: str = ""  # 'Regular', 'Curvilinear', 'Unstructured'
    has_depth: bool = True
    dimensions: tuple = ()
    # timestep_interval: float = "" #'1', '0.5', etc
    # either forecast or hindcast info -- not both
    sources : list = dataclasses.field(default_factory=list)
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
        self.name = m.metadata["long_name"]
        self.description = m.description
        try:
            self.html_desc = m.metadata["html_desc"]
        except KeyError:
            self.html_desc = m.description
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
        self.init_source_metadata(m)
        self.compute_env_params()
        return self

    def init_source_metadata(self, model):
        """initiate metadata"""
        # given a model, extract the source start_end times and set them on self
        all_sources = [k for k in model.keys()]
        for k in all_sources:
            src = model[k]
            srcmeta = SourceMetadata()
            srcmeta.init_from_model_source(src)
            self.sources.append(srcmeta)

    def compute_env_params(self):
        """compute env params"""
        # Computes and sets the list of satisfied environmental parameters
        # An env param is considered satisfied if ALL of fore/now/hindcast can
        # provide that env param.
        self.env_params = self.sources[0].env_params
        for src in self.sources:
            self.env_params = self.env_params & src.env_params

    @staticmethod
    def regional_test(model):
        """
        Selection criteria for 'regional' flag in the metadata
        Effectively, a flag to describe what is a 'large' regional model (HYCOM, GFS) and what isnt
        """
        bb = model.metadata["bounding_box"]
        return abs(bb[2] - bb[0]) > 90 or abs(bb[3] - bb[1]) > 90

    def as_pyson(self):
        """
        returns a JSON compatible dict of the data
        """
        dict_ = dataclasses.asdict(self)
        dict_["env_params"] = list(self.env_params)
        dict_["sources"] = []
        for s in self.sources:
            dict_["sources"].append(s.as_pyson())
        return dict_



    