"""
Core API for accessing model results

These are the functions that the WebGNOME client will call

"""
import datetime
from pathlib import Path
from . import (
    NonIntersectingSubsetError,
    NonIntersectingTimeIntervalError,
    NWS_point,
    models,
    standard_names,
    shoreline,
    utilities,
    config,
)

from .models import metadata


def list_models(model_ids=None,
                map_bounds=None,
                env_params=None,
                as_pyson=True
                ):
    """
    Return metadata for all available models
    This is the static information about the models (typically in a yaml file). It will not include
    actual start/end time based on querying the server

    :param model_ids_sources=None: Optional list of models identifiers. If None all available
                                models will be returned.

    :param map_bounds=None: Bounds within which the models must overlap, if None, the
                            whole world.

    :param env_params=None: Only provide models that have the given parameters. The mapping
                            for env_params is in standard_names and includes
                            "surface currents" etc.

    :param as_pyson=True: If True, result is JSON-compatible dict.
                           If false, Metadata objects.

    :returns: list of metadata for models that satisfy the criteria

    """
    all_metas = models.get_model_metadata()
    retval = utilities.filter_models(
        all_metas,
        model_ids=model_ids,
        map_bounds=map_bounds,
        env_params=env_params,
    )

    if as_pyson:
        retval = [m.as_pyson() for m in retval]

    return retval


def get_model(model_id, start=None, end=None):
    """
    Return model object for a particular model.
    This will instantiate the model object to add the current
    time bounds.

    :param model_id: the name (unique ID) of the model as in `api.list_models()`
    :param start: datetime (optional) used to restrict model output (see note)
    param end: datetime (optional) used to restrict model output time series (see note)

    NOTE: the start/end time is more typically for the local archive where files are
    unaggregated and a MFDataset object is created from a filelist. For aggregated
    model output (e.g. on TDS or zarr) subsetting in time is typically done after
    opening the dataset

    :returns: model obj with metadata of the model converted to dict
    """

    archive_dir = config.archive_dir

    if archive_dir is not None and (archive_dir / model_id.lower()).is_dir():
        model_obj = models.ALL_MODELS[model_id](access='local', start=start, end=end, archive_dir=archive_dir)
        if start is not None:
             model_obj.open_ds()
    else:
        model_obj = models.ALL_MODELS[model_id]()
        model_obj.open_ds() #try/except here?
        if start is not None:
            model_obj.subset_time(start, end) #update actual start/end?

    meta = model_obj.metadata
    meta.actual_start = model_obj.actual_start.isoformat()
    meta.actual_end = model_obj.actual_end.isoformat()

    model_obj.metadata = meta.as_pyson()

    return model_obj


def validate_subset(model_id, start, end, bounds):
    """
    Test the desired subset (in space and time) by ensuring that there is
    overlap with the time bounds and grid bounds of the selected model

    :param model_id: the name (unique ID) of the model as defined in the yaml files
    :param start: start of model output to include (strings in format %Y-%m-%dT%H:%M:%S
                  or datetimes)
    :param end: end of model output to include (strings in format %Y-%m-%dT%H:%M:%S
                or datetimes)
    :param bounds: spatial bounds to subset -- (west, south, east, north)

    :returns: True if the subset is valid, otherwise False
    """

    polybounds = utilities.bbox2polygon(bounds)

    model_obj = get_model(model_id)

    # FIXME: we should probably special-case the global models:
    #        the round earth is a pain!
    if not utilities.subset_intersects_model_boundary(model_obj.metadata["bounding_poly"], polybounds):
        # no overlap in at least one dimension
        raise NonIntersectingSubsetError("Subset does not intersect model boundary")

    if not utilities.check_valid_time_intersection(
        (start, end), (model_obj.metadata["actual_start"], model_obj.metadata["actual_end"])
    ):
        raise NonIntersectingTimeIntervalError("Subset does not intersect model time bounds")

    return True


def get_model_subset(
    model_id,
    start,
    end,
    bounds,
    #surface_only=True,
    cross_dateline=False,
    environmental_parameters=["surface currents"],
    ):
    """
    Determine the indices for the desired subset (in space and time)

    :param model_id: the name (unique ID) of the model as defined in the yaml files
    :param start: start of model output to include (strings in format %Y-%m-%dT%H:%M:%S
                  or datetimes)
    :param end: end of model output to include (strings in format %Y-%m-%dT%H:%M:%S
                or datetimes)
    :param bounds: spatial bounds to subset -- (west, south, east, north)
    :param surface_only: boolean to select only surface values
    :param cross_dateline: boolean to specify dateline cross TODO: check implementation
    :param environmental_parameters: which variables to include - can be a subset of
    ["surface currents", "surface winds", "3D currents", "water properties", "ice"]
    If 3D currents are selected, water properties will be 3D

    """
    # polybounds = utilities.bbox2polygon(bounds)

    if type(start) is not datetime.datetime:
        start = datetime.datetime.fromisoformat(start)
    if type(end) is not datetime.datetime:
        end = datetime.datetime.fromisoformat(end)

    model_obj = get_model(model_id, start=start, end=end)

    if "3D currents" in environmental_parameters:
        surface_only = False
        model_obj.get3d = True  # this is used by nc4 based subclasses
    else:
        surface_only = True
        model_obj.get3d = False

    model_obj.subset_grid(bounds)
    if surface_only:
        try:
            model_obj.select_surface()
             # this is used by nc4 based subclasses
        except AttributeError: #may be surface only output
            pass

    var_list = standard_names.get_standard_names(environmental_parameters)
    model_obj.filter_variables(var_list)

    if not hasattr(model_obj,'ds'):
        model_obj.make_xr_dataset()

    return model_obj


def get_model_output(model_obj, output_pth):
    """
    Get the model output based on the subset information
    """
    output_path = model_obj.write_nc(output_pth)

    return output_path


def NWS_point_wind(lon, lat):
    data = NWS_point.get_data(lon, lat)
    if "err" in data.keys():
        raise ValueError(data["err"])
    else:
        json_data = NWS_point.format_JSON(data)
    return json_data


def get_map(
    bounds,
    data_source="gshhs",
    ofn="coast.bna",
    resolution="h",
    cross_dateline=False,
    max_filesize=1e6,
):
    """
    This is for compatibility with current implementation in API which was expecting a file
    delivered from a URL Also need to think about how to test for max filesize differently since
    now its being written directly to server
    """

    shoreline.get_map(bounds, data_source, ofn, resolution, cross_dateline, max_filesize)
    filename = ofn
    contents = open(filename).read()

    return filename, contents
