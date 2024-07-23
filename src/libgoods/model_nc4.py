"""
This leverages Amy's old libGOODS code to determine subset size and write the output
"""

from . import file_processing
import numpy as np


def get_time_bounds(url, tvar):
    """
    Determine the start/end times
    """

    model = file_processing.base.nc()
    model.open_nc(FileName=url, tvar=tvar)

    return model.start_date, model.end_date


def get_model_subset(
    url,
    start,
    end,
    bounds,
    var_dict,
    surface_only=True,
    cross_dateline=False,
    grid=None,
):
    """
    TO DO: THIS IS OUT OF DATE
    :param model_id: ID (name) of the model
    :param model_source (forecast/nowcast etc) -- !!!naming conventions are changing soon
    :params start: start time of to subset to (date string)
    :params end: end time to subset to (date string)
    :param bounds: bounds to subset to -- (using [x1,y1,x2,y2] format at present
    :param surface_only: limit to surface values in model output
    :param cross_dateline=False: whether the subset crosses the dateline
    :param environmental_parameters: which environmental parameters to extract

    :returns: file processing model object
    """
    # source = mc.select_date_range(cat[model_source], start_date=start, end_date=end)
    if grid == "unstructured":
        pass  # not implemented yet
    elif grid == "curvilinear":
        if 'longitude' in var_dict:
            model = file_processing.curv()
        else:
            model = file_processing.roms()
    elif grid == 'rectangular':
        model = file_processing.rect()
    else:
        raise KeyError(
            "Grid must be specified as unstructured, curvilinear, or rectangular"
        )

    model.open_nc(url)
    # get dimensions to determine subset
    if surface_only:
        model.get_dimensions(var_map=var_dict)
    else:
        model.get_dimensions(var_map=var_dict,get_z=True)
    if model.lon.max() > 180:  # should model catalogs tell us the coordinates?
        bounds[0] = np.mod(bounds[0] + 360, 360)
        bounds[2] = np.mod(bounds[2] + 360, 360)

    t1, t2 = model.get_timeslice_indices(start, end)
    # grid subsetting
    model.subset(bounds)
    # model.write_nc(var_map=var_map, ofn=target_pth, t_index=[t1, t2, 1])

    # strip Dataset so it can be pickled and add source urlpath and other params
    model.Dataset = None
    model.GridDataset = None
    model.urlpath = url
    model.tindex = [t1, t2, 1]
    model.nbytes = 1000  # api will look for this -- have to figure out how to add something
    model.is3d = not (surface_only)
    model.var_map = var_dict

    return model


def write_model_output(model, output_pth, dl=False):

    model.update(model.urlpath
                 )  # this was removed for api (nc4 Dataset can't be pickled)
    model.write_nc(var_map=model.var_map,
                   ofn=output_pth,
                   t_index=model.tindex,
                   is3d=model.is3d,
                   dl=dl)
