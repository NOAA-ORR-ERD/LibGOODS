"""
Core API for accessing model results

These are the functions that the WebGNOME client will call

NOTE: These really need to be refactored to not hit any servers.

Mocking, local, cache, etc.

"""

from . import (
    NonIntersectingSubsetError,
    NonIntersectingTimeIntervalError,
    NWS_point,
    NDBC,
    config,
    models,
    shoreline,
    standard_names,
    utilities,
)


def list_model_names():
    """
    return a list of all the available models id and name
    """
    return([f"{model.identifier}: {model.name} -- {model.long_name}"
            for model in list_models(as_pyson=False)])

def list_models(model_ids=None,
                map_bounds=None,
                env_params=None,
                as_pyson=True
                ):
    """
    Return metadata for all available models
    This is the static information about the models (typically a yaml file).
    It will not include actual start/end time based on querying the server.

    :param model_ids=None: Optional list of models identifiers.
                                   If None all available models
                                   will be returned.

    :param map_bounds=None: Bounds within which the models must overlap,
                            if None, the whole world.

    :type map_bounds: polygon - list of (lon, lat) points. If two points,
                      it's taken as a bounding rect.

    :param env_params=None: Only provide models that have the given parameters.
                            The mapping for env_params is in standard_names
                            and includes "surface currents" etc.

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

    :param model_id: the name (unique ID) of the model
                     as in `api.list_models()`

    :param start: datetime (optional) used to restrict model output (see note)

    :param end: datetime (optional) used to restrict model output time series
                (see note)

    NOTE: the start/end time is more typically for the local archive where
    files are unaggregated and a MFDataset object is created from a filelist.
    For aggregated model output (e.g. on TDS or zarr) subsetting in time is
    typically done after opening the dataset

    :returns: model obj with metadata of the model converted to dict

    NOTE: models using the local archive do not have an xarray ds attached
    unless the start date is not None - this is to avoid opening a really large
    multi file dataset. For external (TDS/OpenDAP sources) we need to open the ds
    to get the actual start/end. This makes the API a bit inconsistent.
    """

    archive_dir = config.archive_dir
    if archive_dir is not None and (archive_dir / model_id.lower()).is_dir():
        model_obj = models.ALL_MODELS[model_id](access='local',
                                                start=start,
                                                end=end,
                                                archive_dir=archive_dir)
        if start is not None:
            model_obj.open_ds()
    else:
        model_obj = models.ALL_MODELS[model_id]()
        model_obj.open_ds()  # try/except here?
        if start is not None:
            model_obj.subset_time(start, end)  # update actual start/end?

    meta = model_obj.metadata
    meta.actual_start = model_obj.actual_start.isoformat()
    meta.actual_end = model_obj.actual_end.isoformat()

    return model_obj


def validate_subset(model_id, start, end, subset_bounds):
    """
    Test the desired subset (in space and time) by ensuring that there is
    overlap with the time bounds and grid bounds of the selected model

    :param model_id: the name (unique ID) of the model
    :param start: start of model output to include
                  (strings in format %Y-%m-%dT%H:%M:%S
                  or datetimes)
    :param end: end of model output to include
                (strings in format %Y-%m-%dT%H:%M:%S
                or datetimes)
    :param subset_bounds: spatial bounds to subset, list of polygon points
           if a bounding box: ((w,s), (w,n), (e,n), (e,s))
           currently the bounding box of a polygon is used.

    :returns: True if the subset is valid, otherwise False
    """

    # polybounds = utilities.bbox2polygon(bounds)
    subset_bounds = utilities.polygon2bbox(subset_bounds)
    subset_bounds = utilities.bbox2polygon(subset_bounds)
    model_obj = get_model(model_id)

    # FIXME: we should probably special-case the global models:
    #        the round earth is a pain!
    if not utilities.subset_intersects_model_boundary(
                        model_obj.metadata.bounding_poly,
                        subset_bounds):
        # no overlap in at least one dimension
        raise NonIntersectingSubsetError(
            "Subset does not intersect model boundary")

    if not utilities.check_valid_time_intersection(
                (start, end),
                (model_obj.actual_start,
                    model_obj.actual_end)
                ):
        raise NonIntersectingTimeIntervalError(
            "Subset does not intersect model time bounds")

    return True


def get_model_subset(
    model_id,
    start,
    end,
    bounds,
    cross_dateline=False,
    environmental_parameters=["surface currents"],
        ):
    ## Fixme: there's a fair bit of logic here, does this belong in the API?
    """

    Get a libgoods model, set up to provide the required subset


    :param model_id: the identifier (unique ID) of the model

    :param start: start of model output to include
                  string in ISO format (%Y-%m-%dT%H:%M:%S)
                  or datetime

    :param end: end of model output to include
                string in ISO format (%Y-%m-%dT%H:%M:%S)
                or datetime

    :param bounds: spatial bounds to subset: vertices of a polygon
                   [(lon, lat), (lon, lat), (lon, lat), (lon, lat)]
                   or two corners of a bounding box:
                   [(min_lon, min_lat), (max_lon, max_lat)]

                   Currently the bounding box of the polygon is used.

                   Proper polygons might be supported in the future.

    :param cross_dateline: boolean to specify dateline cross
           TODO: check implementation

    :param environmental_parameters: which variables to include -
            can be a subset of ["surface currents", "surface winds",
            "3D currents", "water properties", "ice"]
            If 3D currents are selected, water properties will be 3D.

            Default is ["surface_currents"]

    :returns: libgoods model object, ready to be subset.

    """
    # we use subset_bbox in xarray_subset_grid so we need to
    #    (there is a subset_polygon but I haven't tested)
    bounds = utilities.polygon2bbox(bounds)
    bounds = utilities.flatten_bbox(bounds)

    start = utilities.asdatetime(start)
    end = utilities.asdatetime(end)
    # if type(start) is not datetime.datetime:
    #     start = datetime.datetime.fromisoformat(start)
    # if type(end) is not datetime.datetime:
    #     end = datetime.datetime.fromisoformat(end)

    model_obj = get_model(model_id, start=start, end=end)

    if "3D currents" in environmental_parameters:
        get3d = True
    else:
        get3d = False

    var_list = standard_names.get_standard_names(environmental_parameters)
    model_obj.filter_variables(var_list, get3d=get3d)

    model_obj.subset_grid(bounds)
    if not get3d:
        try:
            model_obj.select_surface()
        except ValueError:
            pass

    if not cross_dateline:
        model_obj.normalize_longitude()

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
    This is for compatibility with current implementation in API which
    was expecting a file delivered from a URL Also need to think about
    how to test for max filesize differently since
    now its being written directly to server
    """
    bounds = utilities.flatten_bbox((bounds[0], bounds[2]))

    shoreline.get_map(bounds, data_source, ofn,
        resolution, cross_dateline, max_filesize)
    filename = ofn
    contents = open(filename).read()

    return filename, contents


def get_NDBC_wind(station, tz_offset="00", number_days_ago=45):

    wind_data = NDBC.get_recent_data_from_url(station, tz_offset, number_days_ago)
    json_data = NDBC.format_JSON(wind_data)
    json_data['buoy_id'] = station
    return json_data
