"""
Core API for accessing model results

These are the functions that the WebGNOME client will call

Functions return JSON-compatible dicts
"""

from pathlib import Path
from .current_sources import all_currents
from .dummy_sources import all_dummy_sources
from . import utilities
from . import FileTooBigError


# all_models is a dict with
#   key: name of model
#   value: DataSource object
all_models = {}
all_models.update(all_currents)
all_models.update(all_dummy_sources)
# there will be many more in the future




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
