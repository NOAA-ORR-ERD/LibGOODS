"""
Core API for accessing model results

These are the functions that the WebGNOME client will call

Functions return JSON-compatible dicts
"""

from pathlib import Path
import warnings
from shapely.geometry import Polygon, MultiPoint

# import shapely.wkt as wkt
# from . import utilities
from . import FileTooBigError
from .model import ENVIRONMENTAL_PARAMETERS, Metadata

import numpy as np


try:
    import model_catalogs as mc

    env_models = mc.setup_source_catalog()
    all_metas = {m: Metadata().init_from_model(env_models[m]) for m in env_models}
except ImportError:
    warnings.warn("model_catalogs not found: libgoods API will not work")


##################
# utility functions -- implementation, not API
##################


def _filter_by_env_params(mdl_meta, ev_p):
    """
    :param mdl_meta: model Metadata object
    :param ev_p: list of environmental parameter (string) or singular string
    """
    # filter models out if they do not have required env_params
    if not (isinstance(ev_p, list) or isinstance(ev_p, tuple)):
        # assume singular string
        if ev_p not in ENVIRONMENTAL_PARAMETERS.keys():
            raise KeyError("{} is not a valid environmental parameter".format(ev_p))
        return ev_p in mdl_meta.env_params
    else:
        # assume multiple filter parameters eg ['surface currents', 'surface winds']
        return all([param in mdl_meta.env_params for param in ev_p])


def _filter_by_poly_bounds(mdl_meta, poly_bounds):
    """
    :param mdl_meta: model Metadata object
    :param poly_bounds: shapely Polygon boundary.
           Coords must be in (-180, -90), (180, 90) range
    """
    bb = np.array(mdl_meta.bounding_box)
    if np.any(bb > 180):
        bb[0] -= 180
        bb[2] -= 180
    bb_poly = MultiPoint([(bb[0], bb[1]), (bb[2], bb[3])]).envelope
    return bb_poly.intersects(poly_bounds)


def filter_models(models_metadatas, map_bounds=None, name_list=None, env_params=None):
    """
    Filters a provided list of model metadata via three criteria:
    1. Intersects with provided polygon boundary
    2. A name list
    3. Present environmental parameters

    :param models_metadatas: list of model Metadata objects
    :param poly_bounds: list of tuples (coordinates), or shapely Polygon, or None
    :param name_list: list of string names of models
    :param env_params: string eg 'surface_currents' or list of string eg ['surface_currents', '3D_temperature']
        see libgoods.model.ENVIRONMENTAL_PARAMETERS for valid query strings
    """
    retlist = models_metadatas
    if name_list is not None:
        retlist = [m for m in retlist if m.identifier in name_list]

    if map_bounds is not None:
        map_bounds = (
            Polygon(map_bounds) if not isinstance(map_bounds, Polygon) else map_bounds
        )
        retlist = [m for m in retlist if _filter_by_poly_bounds(m, map_bounds)]

    if env_params is not None:
        retlist = [m for m in retlist if _filter_by_env_params(m, env_params)]

    return retlist


###########
# API functions -- these are what WebGNOME will call
###########


def list_models(name_list=None, map_bounds=None, env_params=None, as_pyson=False):
    """
    Return metadata for all available models

    This is the static information about the models

    :param name_list=None: Optional list of particular models names. If None
                           all available models will be returned
    :param map_bounds: Bounds within which the models can overlap, if None, the whole world

    :param env_params=None: Only provide models that have the given parameters

    :param as_pyson=False: If True, result is JSON-compatible dict.
                           If false, Metadata objects.

    :returns: list of metadata for models that satisfy the criteria

    """
    retval = filter_models(
        all_metas.values(),
        name_list=name_list,
        map_bounds=map_bounds,
        env_params=env_params,
    )
    if as_pyson:
        retval = [m.as_pyson() for m in retval]
    return retval


def get_model_info(model_name):
    """
    Return metadata about a particular model

    :param model_name: the name (unique ID) of the model.

    :returns: libgoods.models.Metadata object with metadata of the model.

    """
    if model_name not in env_models:
        raise KeyError(f"{model_name} is not a valid model name")
    else:
        return Metadata(model=env_models[model_name])


def get_model_subset_info(
    model_id,
    bounds,
    time_interval,
    environmental_parameters,
    cross_dateline=False,
):
    """
    Return the primary information about a model subset:

    {"grid_type":
     "num_grid_cells":
     "num_timesteps":
     "estimated_file_size":
    }
    NOTE: this could be different depending on grid type

    """
    return all_models[model_id].get_model_subset_info(
        bounds,
        time_interval,
        environmental_parameters,
        cross_dateline=False,
    )


def get_model_data(
    model_id,
    bounds,  # polygon list of (lon, lat) pairs
    time_interval,
    environmental_parameters,
    cross_dateline=False,
    max_filesize=None,
    target_dir=None,
):
    """
    Get the actual model data as a netcdf file.

    :param model_id: ID (name) of the model
    :param bounds: bounds to subset to -- if the implementation doesn't
                   support polygons, the bonding box of the bounds will be used.
    :param time_interval: time span to subset to -- pair of datetime objects

    :param environmental_parameters: which environmental parameters to extract

    :param cross_dateline=False: whether the subset crosses the dateline

    :param max_filesize = None: maximum filesize to generate -- if the file will
                          be larger than this, raise a FileTooBigError

    :param target_dir: directory to write the file too -- if None, it will be put
                       in a temp dir or local dir.


    :returns: Path object for the file
    """

    if target_dir is not None:
        target_dir = Path(target_dir)

    # NOTE: this implementation may not be appropriate
    source = all_models[model_id]

    filepath = source.get_data(
        bounds,  # polygon list of (lon, lat) pairs
        time_interval,
        environmental_parameters,
        cross_dateline,
        max_filesize,
        target_dir,
    )

    return Path(filepath)
