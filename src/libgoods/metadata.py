"""
Base classes for the core data models

Static Model metadata:

{'name': self.name,
 'bounding_box': self.bounding_box, # (lower_left, upper_right)
 'bounds': self.bounds, # thinned polygon ~ 100 points
 'info_text': self.info_text
 'forecast_available': True
 'hindcast_available': False
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

import yaml
import dataclasses
from pathlib import Path
import shapely.wkt as wkt
from shapely.geometry.multipolygon import MultiPolygon
from .standard_names import get_env_params

yaml_file_directory = Path(__file__).parent / 'yaml_files'


def get_all_metadata():
    """
    Loop though all the files in the yaml files directory and return a
    dict of the metadata for all models
    """

    flist = yaml_file_directory.glob('*.yaml')
    all_metas = {
        f.name.split('.')[0].upper(): Metadata().init_from_yaml(f)
        for f in flist
    }
    return (all_metas)


def get_metadata_for_model(model, source):
    """
    Return the metadata for a particular model/source

    """

    yaml_file = Path(yaml_file_directory, model.lower() + '.yaml')
    meta = Metadata().init_from_yaml(yaml_file, source=source).as_pyson()

    return (meta)




@dataclasses.dataclass
class Metadata:
    identifier: str = ""
    name: str = ""
    description: str = ""
    html_desc: str = ""
    regional: bool = False
    bounding_box: tuple = ()
    bounding_poly: tuple = ()
    grid_type: str = ""  # 'Rectangular', 'Curvilinear', 'Unstructured'
    has_depth: bool = True
    dimensions: tuple = ()
    sources: list = dataclasses.field(default_factory=list)
    env_params: set = dataclasses.field(default_factory=set)
    """
    class to hold the core meta data for a data source

    This could include validation, or ...

    Currently this has defaults for everything, but maybe it should require everything?
    """

    def init_from_yaml(self, yaml_file, source=None):
        """initiate a model"""
        # given a model, extract the data and set on self. If source is None,
        # get metadata for all sources

        with open(yaml_file, 'r') as file:
            model_info = yaml.full_load(file)
        yaml_bdry_file = yaml_file_directory / 'boundaries' / yaml_file.name
        try:
            with open(yaml_bdry_file, 'r') as file:
                model_info.update(yaml.full_load(file))
            self.bounding_box = model_info["bbox"]
            self.regional = Metadata.regional_test(self.bounding_box)
            bounding_poly = wkt.loads(model_info["wkt"])
            if isinstance(bounding_poly, MultiPolygon):
                bounding_poly = bounding_poly.convex_hull
            self.bounding_poly = list(bounding_poly.boundary.coords)
        except FileNotFoundError:
            print('No boundary information available for this model')
        self.identifier = model_info["name"]
        self.name = model_info["metadata"]["long_name"]
        self.description = model_info["description"]
        try:
            self.html_desc = model_info["metadata"]["html_desc"]
        except KeyError:
            self.html_desc = self.description
        
        self.grid_type = model_info["metadata"]["grid_type"]
        grid_dim_keyname = [
            n for n in model_info["metadata"].keys() if "grid_dim_" in n
        ][0]
        self.has_depth = len(model_info["metadata"][grid_dim_keyname]) == 4
        self.dimensions = model_info["metadata"][grid_dim_keyname]
        self.init_source_metadata(model_info["sources"], source=source)
        self.compute_env_params()
        return self

    def init_source_metadata(self, sources, source):
        """initiate metadata"""
        # given a model, extract the source start_end times and set them on self

        if source is not None:
            all_sources = [
                source,
            ]
        else:
            all_sources = sources.keys()
        for k in all_sources:
            src = sources[k]
            srcmeta = SourceMetadata(name=k)
            srcmeta.init_from_dict(src)
            self.sources.append(srcmeta)

    def compute_env_params(self):
        """compute env params"""
        # Computes and sets the list of satisfied environmental parameters
        # An env param is considered satisfied if ALL of fore/now/hindcast can
        # provide that env param
        self.env_params = self.sources[0].env_params
        for src in self.sources:
            self.env_params = self.env_params & src.env_params

    @staticmethod
    def regional_test(bb):
        """
        Selection criteria for 'regional' flag in the metadata
        Effectively, a flag to describe what is a 'large' regional model (HYCOM, GFS) and what isnt
        """
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


@dataclasses.dataclass
class SourceMetadata:
    """source metadata"""

    # metadata for a particular model source
    # axis: dict = dataclasses.field(default_factory=dict)
    #              'dim_x -> [grid_variable_x]
    name: str = ""
    period: float = (0, )  # output period in hours
    start: str = ""  # human readable timespan: e.g. "7 days in the past"
    end: str = ""  # human readable timespan
    # dict associating CF name to variable name in data
    standard_names: dict = dataclasses.field(default_factory=dict)
    env_params: set = dataclasses.field(default_factory=set)
    args: dict = dataclasses.field(default_factory=dict)

    def init_from_dict(self, src):
        self.period = src["metadata"]["output_period_(hr)"]
        self.start = src["metadata"]["overall_start_datetime"]
        self.end = src["metadata"]["overall_end_datetime"]
        self.standard_names = src["metadata"]["standard_names"]
        self.env_params = get_env_params(src["metadata"]["standard_names"])
        self.args = src["args"]
        return self

    def as_pyson(self):
        """
        returns a JSON compatible dict of the data
        """
        dict_ = dataclasses.asdict(self)
        dict_["env_params"] = list(self.env_params)
        return dict_
