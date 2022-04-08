"""
Core API for accessing model results

These are the functions that the WebGNOME client will call

Functions return JSON-compatible dicts
"""

from pathlib import Path
from shapely.geometry import Polygon, MultiPoint
import shapely.wkt as wkt
from .current_sources import all_currents
from .dummy_sources import all_dummy_sources
from . import utilities
from . import FileTooBigError
from .model import Metadata

import model_catalogs as mc


# all_models is a dict with
#   key: name of model
#   value: Model object
all_models = {}
all_models.update(all_currents)
all_models.update(all_dummy_sources)
# there will be many more in the future

env_models = mc.setup_source_catalog()

def filter_models(poly_bounds):
    """
    Given a polygon, return the models that intersect with the polygon.
    """
    if not isinstance(poly_bounds, Polygon):
        poly_bounds = Polygon(poly_bounds)

    models = [model.get_metadata() for model in all_models.values()
                if Polygon(model.get_metadata()['bounding_poly']).intersects(poly_bounds)]

    return models

def filter_models2(poly_bounds, name_list=None):
    """
    Given a polygon, return the models that bounding_box intersect with the polygon.
    However, this goes to the catalog and returns a list of catalog entries
    """
    if name_list is None:
        name_list = list(env_models)
    if not isinstance(poly_bounds, Polygon):
        if poly_bounds is None:
            poly_bounds = [(-180,-89), (-180,89), (180, 89), (180, -89)]
        poly_bounds = Polygon(poly_bounds)
    retlist = []
    for m in name_list:
        bb = env_models[m].metadata['bounding_box']
        bb_poly = MultiPoint([(bb[0],bb[1]),(bb[2],bb[3])]).envelope
        if bb_poly.intersects(poly_bounds):
            retlist.append(env_models[m])
    
    return retlist

def list_models2(name_list=None):
    if name_list is None:
        name_list = list(env_models)
    return [env_models[m] for m in name_list]

def extract_API_metadata(models):
    '''
    for a list of catalog entries, return a list of metadata in the expected API format
    '''
    def regional_test(model):
        bb = model.metadata['bounding_box']
        return abs(bb[2]-bb[0]) > 10 or abs(bb[3]-bb[1]) > 10

    retval = []
    for m in models:
        entry = Metadata()
        entry.identifer = m.name
        entry.name = m.description
        entry.regional = regional_test(m)
        bb = m.metadata['bounding_box']
        entry.bounding_box = [(a, b) for a, b in zip(bb[::2],bb[1::2])]
        entry.bounding_poly = list(wkt.loads(m.metadata['geospatial_bounds']).boundary.coords)
        #there are more, but I don't know how to get at them yet.
        retval.append(entry.as_pyson())
    return retval


def list_models():
    """
    Return metadata for all available models

    This is static data
    """
    return [model.get_metadata() for model in all_models.values()]


def get_model_info(model_name):
    """
    Return information about a particular model

    This is all the same metadata as above, plus
    extra data that may require querying the source
    e.g. available model times
    """
    # return {'available_times': (start_time, end_time),
    #        }
    try:
        return all_models["model_name"].get_model_info()
    except KeyError:
        return {"error": f"Model: {model_name} does not exist"}


# NOTE: subset information should be cached so that subsequent
#       call to get_model_data with same params will reuse the
#       computed grid subsetting info


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

    if target_dir is not None:
        target_dir = Path(target_dir)

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
