"""
Core API for accessing model results

These are the functions that the WebGNOME client will call

"""

from . import (
    ModelAvailabilityError,
    NonIntersectingSubsetError,
    NonIntersectingTimeIntervalError,
    utilities,
)

from . import model_nc4 as model
from . import NWS_point, shoreline
from .standard_names import get_standard_names
from . import models
from .models import metadata

def list_models(model_ids=None,
                map_bounds=None,
                env_params=None,
                ):
    """
    Return metadata for all available models
    This is the static information about the models (in yaml file). It will not include
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
    all_metas = models.get_model_metadata(model_ids)
    retval = utilities.filter_models(
        all_metas,
        model_ids=model_ids,
        map_bounds=map_bounds,
        env_params=env_params,
    )

    retval = [m.as_pyson() for m in retval]

    return retval


def get_model_info(model_id, model_source):
    """
    Return metadata about a particular model from a particular source. This will
    query the server to add the actual time bounds to the metadata

    :param model_id: the name (unique ID) of the model as defined in the yaml files
    :param model_source: the source the model output is being requested from

    :returns: libgoods.metadata.Metadata object with metadata of the model and source.
    """
    meta = metadata.get_metadata_for_model(model_id, model_source)

    tvar_name = meta["sources"][0]["standard_names"]["time"]
    meta["urlpath"] = meta["sources"][0]["args"]["urlpath"]
    try:
        stime, etime = model.get_time_bounds(meta["urlpath"], tvar_name)
    except:
        raise ModelAvailabilityError(
            "Unable to retrieve data from server. Please check availability or try again later."
        )

    meta["actual_start"] = stime
    meta["actual_end"] = etime

    return meta


def validate_subset(model_id, model_source, start, end, bounds):
    """
    Test the desired subset (in space and time) by ensuring that there is
    overlap with the time bounds and grid bounds of the selected model

    :param model_id: the name (unique ID) of the model as defined in the yaml files
    :param model_source: the source the model output is being requested from
    :param start: start of model output to include (strings in format %Y-%m-%dT%H:%M:%S
                  or datetimes)
    :param end: end of model output to include (strings in format %Y-%m-%dT%H:%M:%S
                or datetimes)
    :param bounds: spatial bounds to subset -- (west, south, east, north)

    :returns: True if the subset is valid, otherwise False
    """

    polybounds = utilities.bbox2polygon(bounds)

    meta = get_model_info(model_id, model_source)
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

    meta = get_model_info(model_id)

    # build url list if unaggregated
    if "noagg" in model_source:
        pass

    else:
        urlpath = meta["urlpath"]

    # these are what we want to include
    snames_list = get_standard_names(environmental_parameters)
    snames_dict = meta["sources"][0]["standard_names"]
    var_dict = {x: snames_dict[x] for x in snames_list if x in snames_dict}
    ds = model.get_model_subset(
        urlpath,
        start,
        end,
        list(bounds),
        surface_only=surface_only,
        cross_dateline=cross_dateline,
        var_dict=var_dict,
        grid=meta["grid_type"],
    )

    ds.cross_dateline = cross_dateline

    return ds


def get_model_output(xds, output_pth):
    """
    Get the model output based on the subset information
    """
    output_path = model.write_model_output(xds, output_pth, dl=xds.cross_dateline)

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
    This is for compatibility with current implementation in API which was expecting a file delivered from a URL
    Also need to think about how to test for max filesize differently since now its being written directly to server
    """

    shoreline.get_map(bounds, data_source, ofn, resolution, cross_dateline, max_filesize)
    filename = ofn
    contents = open(filename).read()

    return filename, contents
