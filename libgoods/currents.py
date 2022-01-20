from pathlib import Path
from .current_sources import all_currents
from . import utilities

MODEL_TYPES = {'currents', 'winds'}


def list_models(type):
    '''
    list all available models

    type is one of {'currents', 'winds'}
    '''
    if type not in MODEL_TYPES:
        raise ValueError(f"{type} is not supported. Supported types are:"
                         f"{MODEL_TYPES}")
    if type == 'winds':
        raise NotImplementedError('winds not yet supported')
    elif type == 'currents':
        data = [model.get_metadata() for model in all_currents.values()]

    return data


def get_currents(model_name,
                 north_lat,
                 south_lat,
                 west_lon,
                 east_lon,
                 cross_dateline=False,
                 max_filesize=None,
                 ):

    source = all_currents[model_name]

    # probably need to update the API to use bounds
    # but converting here.

    bounds = utilities.bbox2polygon((south_lat, west_lon, north_lat, east_lon))

    filepath = source.get_data(bounds,
                               cross_dateline,
                               max_filesize)

    # just to conform with the current API

    filename = Path(filepath).name
    return filename, filepath
