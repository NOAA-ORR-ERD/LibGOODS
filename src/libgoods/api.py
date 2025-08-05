"""
Core API for accessing model results

These are the functions that the WebGNOME client will call

"""
import datetime
from pathlib import Path
from . import (
    ModelAvailabilityError,
    NonIntersectingSubsetError,
    NonIntersectingTimeIntervalError,
    NWS_point,
    models,
    shoreline,
    utilities,
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

def get_model_info(model_id, archive_dir=None):
    """
    Return metadata about a particular model from a particular source. This will
    instantiate the model object to add the actual time bounds to the metadata

    :param model_id: the name (unique ID) of the model as defined in the yaml files
    :returns: libgoods.metadata.Metadata object with metadata of the model
    """
    meta = models.get_model_metadata(model_id)[0]
    local_model_dir = Path("/path/to/nonexistent/file.txt")
    # FIXME -- I need to figure out the logic for this to allow
    # an archive_dir to exist but not include a specific model
    if archive_dir is not None:
        local_model_dir = Path(archive_dir) / model_id.lower()
    if local_model_dir.exists():
        model_obj = models.ALL_MODELS[model_id](access='local', archive_dir=archive_dir)
    else:
        model_obj = models.ALL_MODELS[model_id]()
        model_obj.open_ds() #try/except here?
        model_obj.get_start_end()

    meta.actual_start = model_obj.actual_start.isoformat()
    meta.actual_end = model_obj.actual_end.isoformat()

    """     tvar_name = meta["sources"][0]["standard_names"]["time"]
    meta["urlpath"] = meta["sources"][0]["args"]["urlpath"]
    try:
        # is calling get_time_bounds the right way to check if it's valid ??
        stime, etime = model.get_time_bounds(meta["urlpath"], tvar_name)
    except:  # what exceptions might we get here??
        raise ModelAvailabilityError(
            "Unable to retrieve data from server. Please check availability or try again later."
        ) """

    return meta.as_pyson()


def validate_subset(model_id, start, end, bounds, archive_dir=None):
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

    meta = get_model_info(model_id, archive_dir=archive_dir)
    # FIXME: we should probably special-case the global models:
    #        the round earth is a pain!
    if not utilities.subset_intersects_model_boundary(meta["bounding_poly"], polybounds):
        # no overlap in at least one dimension
        raise NonIntersectingSubsetError("Subset does not intersect model boundary")

    if not utilities.check_valid_time_intersection(
        (start, end), (meta["actual_start"], meta["actual_end"])
    ):
        raise NonIntersectingTimeIntervalError("Subset does not intersect model time bounds")

    return True


def get_model_subset(
    model_id,
    start,
    end,
    bounds,
    surface_only=True,
    cross_dateline=False,
    environmental_parameters=["surface currents"],
    archive_dir=None
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
    :param environmental_parameters: which variables to include, e.g.,
                                     "surface currents" - see standard_names for mapping
    """
    # polybounds = utilities.bbox2polygon(bounds)
    if "3D currents" in environmental_parameters:
        surface_only = False
    else:
        surface_only = True

    if type(start) is not datetime.datetime:
        start = datetime.datetime.fromisoformat(start)
    if type(end) is not datetime.datetime:
        end = datetime.datetime.fromisoformat(end)

    local_model_dir = Path("/path/to/nonexistent/file.txt")
    # FIXME -- I need to figure out the logic for this to allow
    # an archive_dir to exist but not include a specific model
    if archive_dir is not None:
        local_model_dir = Path(archive_dir) / model_id.lower()

    if local_model_dir.exists():
        model_obj = models.ALL_MODELS[model_id](access='local', start=start, end=end, archive_dir=archive_dir)
        model_obj.open_ds()
    else:
        model_obj = models.ALL_MODELS[model_id]()
        model_obj.open_ds()
        model_obj.subset_time(start,end)

    model_obj.subset_grid(bounds)
    if surface_only:
        try:
            model_obj.select_surface()
        except AttributeError: #may be surface only output
            pass
    model_obj.filter_variables()

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
