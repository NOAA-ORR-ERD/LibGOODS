"""
assorted utilities useful for libgoods
"""

import datetime
import warnings

import numpy as np
from shapely.geometry import MultiPoint, Polygon


def get_example_bbox(model_id):
    bboxes = {
        "CBOFS": (-76.5, 36.75, -75.25, 37.75),
        "CBOFS_RGRID": (-76.5, 36.75, -75.25, 37.75),
        "CIOFS": (-154.5, 58.0, -151.0, 60.0),
        "CIOFS_RGRID": (-154.5, 58.0, -151.0, 60.0),
        "CREOFS": (-123.9, 46.1, -123.6, 46.3),
        "CREOFS_RGRID": (-123.9, 46.1, -123.6, 46.3),
        "DBOFS": (-75.5, 38.5, -74.5, 39.25),
        "DBOFS_RGRID": (-75.5, 38.5, -74.5, 39.25),
        "GFS_1_2DEG": (-85.0, 25.0, -60.0, 48.0),
        "GFS-1-4DEG": (-85.0, 25.0, -60.0, 48.0),
        "GFS_1DEG": (-85.0, 25.0, -60.0, 48.0),
        "NECOFS": (-70, 41, -66, 44),
        "GOMOFS": (-70, 41, -66, 44),
        "GOMOFS_2DS": (-70, 41, -66, 44),
        "GOMOFS_RGRID": (-70, 41, -66, 44),
        "HYCOM": (-79.10, 31.84, -68.159, 42.29),
        "LEOFS": (-83.6, 41.5, -82.6, 42.1),
        "LEOFS_RGRID": (-83.6, 41.5, -82.6, 42.1),
        "LMHOFS": (-88, 41.57, -86, 44),
        "LMHOFS_RGRID": (-88, 41.57, -86, 44),
        "LOOFS": (-78.6, 43.4, -77.1, 43.7),
        "LOOFS_RGRID": (-78.6, 43.4, -77.1, 43.7),
        "LSOFS": (-89.4, 47.0, -86.4, 47.75),
        "LSOFS_RGRID": (-89.4, 47.0, -86.4, 47.75),
        "NGOFS2": (-91.5, 29.25, -91, 29.75),
        "NGOFS2_2DS": (-91.5, 29.25, -91, 29.75),
        "NGOFS2_RGRID": (-91.5, 29.25, -91, 29.75),
        "NYOFS": (-74.1, 40.49, -73.95, 40.61),
        "SFBOFS": (-122.55, 37.75, -122.4, 37.9),
        "SFBOFS_RGRID": (-122.55, 37.75, -122.4, 37.9),
        "SSCOFS": (-125.70, 47.71, -123.56, 48.77),
        "TBOFS": (-82.9, 27.3, -82.6, 27.7),
        "TBOFS_RGRID": (-82.9, 27.3, -82.6, 27.7),
        "WCOFS": (-122.0, 25.0, -115.0, 35.0),
        "WCOFS_2DS": (-122.0, 25.0, -115.0, 35.0),
        "WCOFS_RGRID": (-122.0, 25.0, -115.0, 35.0),
    }

    return bboxes[model_id]


def convert_longitude(lon, coord_system="-180--180", normalize=True):
    """
    Convert longitude values to a given coordinate system.

    Options are:

    "-180--180": Negative 180 degrees to 180 degrees

    "0--360": Zero to 360 degrees

    :param lon: numpy array-like of longitude values of float type
    :param  coord_system='-180--180': options are: {"-180--180", "0--360"}

    :param normalize=True: If True:
                           360 converts to 0
                           -180 converts to 180
                           If False, 360 and -180 are preserved.

    It should be safe to call this on any coords -- if they are already
    in the expected format, they will not be changed, except for the
    normalization above.
    """

    if coord_system not in {"-180--180", "0--360"}:
        raise TypeError('coord_system must be one of {"-180--180", "0--360"}')
    lon = np.array(lon)

    if coord_system == "0--360":
        shifted = (lon + 360) % 360
        if not normalize:
            shifted[lon == 360] = 360
        return shifted

    elif coord_system == "-180--180":
        lon = np.array(lon)
        lon[lon > 180] -= 360
        if normalize:
            lon[lon <= -180] += 360
        else:
            lon[lon < -180] += 360
        return lon


def check_valid_latitude(lat):
    """make sure lat is valid"""

    if not (-90.0 < lat < 90.0):
        raise ValueError(f"latitude cannot be larger than 90. Got{lat}")

    return True


def check_valid_longitude(lon, system="all"):
    """
    checks for valid longitude coordinates.

    Only option is 'all': -180 -- 360

    We should implement other options some day:
     - -180 -- 180
     - 0 -- 360
    """
    COORDSYSTEMS = {"all"}
    if system not in {"all"}:
        raise ValueError(f"Invalid coordinate system. Options are: {COORDSYSTEMS}")
    if not (-180.0 <= lon <= 360.0):
        raise ValueError(f"longitude cannot be larger than 360 or less than -180. Got{lon}")

    return True


def check_valid_box(bbox, system="all"):
    """
    checks that longitude and latitude values of a
    bounding box make sense

    bbox is four values: (min_lat, min_lon, max_lat, max_lon)
    """
    check_valid_latitude(bbox[0][1])
    check_valid_latitude(bbox[1][1])
    check_valid_longitude(bbox[0][0], system)
    check_valid_longitude(bbox[1][0], system)
    return True


def check_valid_interval(interval):
    return (interval[0] <= interval[1]) and len(interval) == 2


def check_valid_time_intersection(interval_1, interval_2):
    """
    Checks a time interval against another time interval
    Currently, returns True if both intervals are valid, and
    there is any overlap at all.

    :param interval_1: tuple of 2 datetimes
    :param interval_2: tuple of 2 datetimes
    :returns: bool
    """
    if isinstance(interval_1[0], str):
        interval_1 = [datetime.datetime.fromisoformat(x) for x in interval_1]

    if isinstance(interval_2[0], str):
        interval_2 = [datetime.datetime.fromisoformat(x) for x in interval_2]

    if not check_valid_interval(interval_1):
        raise ValueError("Start is not before or equal to end for interval 1")
    if not check_valid_interval(interval_2):
        raise ValueError("Start is not before or equal to end for interval 2")
    return interval_1[0] <= interval_2[1] and interval_1[1] >= interval_2[0]


def polygon2bbox(bounds):
    """
    converts two or more points to a two pair tuple defining a bounding box:

    In::

        [(lon, lat1),
         (lon2, lat2),
         (lon3, lat3),
         (lon4, lat3),
         ...
         ]
    Out::

    ((min_lon, min_lat), (max_lon, max_lat))
    """
    # FIXME: maybe bounding boxes should be defined in terms of:
    #        ((west, south), (north, east)) rather than min,max
    #        it's kinda the same, except near the dateline
    #        (and maybe the prime meridian)
    #
    #        There is a hacky function: correct_bbox_for_dateline
    #        that maybe should be rolled into this function.
    try:
        bounds = np.asarray(bounds, dtype=np.float64).squeeze()
        bounds = bounds.reshape(-1, 2)
        if len(bounds) < 2:
            raise ValueError("Bounding box requires at least 2 points")
    except ValueError as err:
        raise ValueError("bounds must be pairs of (lon, lat) points") from err
    min_lon, min_lat = bounds.min(axis=0)
    max_lon, max_lat = bounds.max(axis=0)
    return ((min_lon, min_lat), (max_lon, max_lat))


def correct_bbox_for_dateline(bbox, xDateline=None):
    """
    A bounding box should be southwest_corner, northeast_corner

    But if you are using -180 -- 180, then minimum longitude is not west if you cross the dateline

    -- this is what the old GOODs API requires -- for others ???

    If xDateline is None, it will assume you want your bounding box to be
    less than 180 degrees (half the earth)

    bbox in form: In the form: (min_lon, min_lat, max_lon, max_lat)

    """
    if xDateline is None:
        total_lon = bbox[1][0] - bbox[0][0]
        xDateline = total_lon > 180

    if xDateline:
        bbox = ((bbox[1][0], bbox[0][1]), (bbox[0][0], bbox[1][1]))

    return bbox


def bbox2polygon(bbox):
    """
    Converts (W, S, E, N) bounding box to a four point polygon:
    """

    min_lon = bbox[0]
    min_lat = bbox[1]
    max_lon = bbox[2]
    max_lat = bbox[3]

    return [
        (min_lon, max_lat),
        (max_lon, max_lat),
        (max_lon, min_lat),
        (min_lon, min_lat),
    ]


def flatten_bbox(bbox):
    """
    converts (lower-left, upper-right) Boounding Box form to the previous
    flattened form:

    (min_lon, min_lat, max_lon, max_lat)
    """
    min_lon = bbox[0][0]
    min_lat = bbox[0][1]
    max_lon = bbox[1][0]
    max_lat = bbox[1][1]
    return (min_lon, min_lat, max_lon, max_lat)


def _filter_by_env_params(mdl_meta, ev_p):
    """
    :param mdl_meta: model Metadata object
    :param ev_p: list of environmental parameter (string) or singular string
    """
    # filter models out if they do not have required env_params
    if not (isinstance(ev_p, list) or isinstance(ev_p, tuple)):
        # assume singular string
        # Huh? where is ENVIRONMENTAL_PARAMETERS supposed to be from?
        if ev_p not in ENVIRONMENTAL_PARAMETERS.keys():  # noqa
            raise KeyError(f"{ev_p} is not a valid environmental parameter")
        return ev_p in mdl_meta.env_params
    else:
        # assume multiple filter parameters eg ['surface currents', 'surface winds']
        return all(param in mdl_meta.env_params for param in ev_p)


def _filter_by_bb_intersection(mdl_meta, poly_bounds):
    """
    :param mdl_meta: model Metadata object
    :param poly_bounds: shapely Polygon (map) boundary.
           Coords must be in (-180, -90), (180, 90) range
    """
    bb = np.array(mdl_meta.bounding_box)
    if np.any(bb > 180):
        bb[0] -= 180
        bb[2] -= 180
    bb_poly = MultiPoint([(bb[0], bb[1]), (bb[2], bb[3])]).envelope
    return bb_poly.intersects(poly_bounds)


def make_polygon_finer(poly, threshold=30.0):
    """
    Adds vertices to polygon segments to make sure none are longer than
    threshold (in whatever units the vertices are in -- usually degrees)

    This uses the shapely segmentize function.

    NOTE: This is useful (critical) for large bounding boxes that span the earth
          e.g. from point one to point two -- which way around the earth?
          if the points are close together, it's easier for that to be clear.

    :param poly: vertices of polygon
    :type poly: numpy Nx2 array or compatible nested sequence

    :param threshold=30.0: length of longest segment

    :returns poly2: Nx2 numpy array of vertices of "thickened" polygon.
    """
    # make a shapely polygon
    shpoly = Polygon(poly)
    # segmentize it
    shpoly = shpoly.segmentize(max_segment_length=threshold)
    poly2 = np.array(shpoly.boundary.coords)

    return poly2


def subset_intersects_model_boundary(model_bounds, poly_bounds, xDateline=None):
    """
    :param model_bounds: model boundary from metadata - can be in any (allowed)
                         longitude coords.
    :param poly_bounds: shapely Polygon (map) boundary.
           Coords must be in (-180 -- 180) longitude form

    :param xDateline=None: Whether the poly bounds cross the dateline.
                           If None, it is assumed that the bounds are less than 180 degrees.
                           e.g. wrap less than halfway around the earth.
    """
    ## Fixme: it would probably be better to special-case the global models
    # Idea: if the difference between the max and min longitude of the model_bounds
    #       is greater than 180 (or 350? or?) then assume it's a global model,
    #       and don't check the longitude at all.
    # maybe just check max and min lat of the subset poly.
    # OR -- replace longitude of model bounds with -360 and 360
    poly_bounds = np.array(poly_bounds)
    # "thicken" the model  boundary to help with world wrapping issues
    # this *might* help, but does not solve the problem.
    # model_bounds = make_polygon_finer(model_bounds, threshold=30.0)  # np.array(model_bounds)
    model_bounds = np.array(model_bounds)

    # print(poly_bounds)
    # print(model_bounds)

    if np.any(poly_bounds[:, 0] > 180) or np.any(poly_bounds[:, 0] < -180):
        warnings.warn(
            "In subset_intersects_model_boundary: poly_bounds should be in -180--180 coordinates"
        )

    if np.any(model_bounds[:, 0] > 360) or np.any(poly_bounds[:, 0] < -180):
        warnings.warn(
            "In subset_intersects_model_boundary: "
            "model_bounds should be in -180--180 or 0--360 coordinates"
        )

    if xDateline is None:
        # see if it's bigger than 180 degrees in -180 -- 180 space.
        if (poly_bounds[:, 0].max() - poly_bounds[:, 0].min()) >= 180:
            xDateline = True
        else:
            xDateline = False

    if xDateline:  # use 0--360 coords
        model_bounds[:, 0] = convert_longitude(model_bounds[:, 0], "0--360", normalize=False)
        poly_bounds[:, 0] = convert_longitude(poly_bounds[:, 0], "0--360", normalize=False)
    elif poly_bounds[:, 0].min() < 0:  # in western hemisphere: use -180 -- 180 coords
        if (
            model_bounds[:, 0].min() >= 0
            and (model_bounds[:, 0].max() - model_bounds[:, 0].min()) > 300
        ):  # model bounds in 0-360
            # only really works for 0-360 and wrapped around the earth.
            model_bounds[:, 0] -= 180
        else:
            model_bounds[:, 0] = convert_longitude(model_bounds[:, 0], "-180--180", normalize=False)
        # poly should already be in -180 == 180, but won't hurt
        poly_bounds[:, 0] = convert_longitude(poly_bounds[:, 0], "-180--180", normalize=False)
    # else:  # no need to convert.
    print(poly_bounds)
    print(model_bounds)

    poly_bounds_poly = Polygon(poly_bounds)
    model_bounds_poly = Polygon(model_bounds)
    return model_bounds_poly.intersects(poly_bounds_poly)


def filter_models(models_metadatas, map_bounds=None, model_ids=None, env_params=None):
    """
    Filters a provided list of model metadata via three criteria:
    1. Intersects with provided polygon boundary
    2. Model ids
    3. Present environmental parameters

    :param models_metadatas: list of model Metadata objects
    :param map_bounds: list of tuples (coordinates), or shapely Polygon, or None
    :param model_ids_sources: list of ids of models
    :param env_params: string e.g. 'surface_currents' or list of strings
                       e.g. ['surface_currents', '3D_temperature']
                       see libgoods.model.ENVIRONMENTAL_PARAMETERS for valid query strings
    """
    retlist = models_metadatas
    if model_ids is not None:
        retlist = [m for m in retlist if m.identifier in model_ids]

    if map_bounds is not None:
        map_bounds = Polygon(map_bounds) if not isinstance(map_bounds, Polygon) else map_bounds
        retlist = [m for m in retlist if _filter_by_bb_intersection(m, map_bounds)]

    if env_params is not None:
        retlist = [m for m in retlist if _filter_by_env_params(m, env_params)]

    return retlist


# note: Pandas has datetime rounding built in -- maybe we should be using that?
def round_dt_to_seconds(dt):
    """
    Round a datetime object to the nearest seconds
    (remove milliseconnds)

    example::

    In [6]: dt = datetime.datetime(2023, 10, 20, 12, 5, 10, 6234)

    In [7]: dt.isoformat()
    Out[7]: '2023-10-20T12:05:10.006234'

    In [8]: round_dt_to_seconds(dt).isoformat()
    Out[8]: '2023-10-20T12:05:10'

    """
    dt += datetime.timedelta(seconds=0.5)
    return dt.replace(microsecond=0)


def round_dt_to_minutes(dt):
    """
    Round a datetime object to the nearest minute
    (remove seconds)

    example::

    In [16]: dt = datetime.datetime(2023, 10, 20, 12, 5, 30, 6234)

    In [17]: dt.isoformat()
    Out[17]: '2023-10-20T12:05:30.006234'

    In [18]: round_dt_to_minutes(dt).isoformat()
    Out[18]: '2023-10-20T12:06:00'

    NOTE: It would be good to have this be rounded to an arbitrary number of minutes
    """

    dt += datetime.timedelta(seconds=30)
    return dt.replace(microsecond=0).replace(second=0)


def round_dt_to_hours(dt):
    """
    Round a datetime object to the nearest hour
    (remove minutes and seconds)

    example::

    In [16]: dt = datetime.datetime(2023, 10, 20, 12, 5, 30, 6234)

    In [17]: dt.isoformat()
    Out[17]: '2023-10-20T12:05:30.006234'

    In [18]: round_dt_to_minutes(dt).isoformat()
    Out[18]: '2023-10-20T12:00:00'
    """

    dt += datetime.timedelta(minutes=30)
    return dt.replace(microsecond=0).replace(second=0).replace(minute=0)
