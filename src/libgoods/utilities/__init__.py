"""
assorted utilities useful for libgoods
"""
import datetime
import re
import numpy as np

from shapely.geometry import Polygon, MultiPoint
import pandas as pd
import fnmatch
import datetime


def get_example_bbox(model_id):

    bboxes = {
        "CBOFS": (-76.5, 36.75, -75.25, 37.75),
        "CBOFS-REGULARGRID": (-76.5, 36.75, -75.25, 37.75),
        "CIOFS": (-154.5, 58.0, -151.0, 60.0),
        "CIOFS-REGULARGRID": (-154.5, 58.0, -151.0, 60.0),
        "CREOFS": (-123.9, 46.1, -123.6, 46.3),
        "CREOFS-REGULARGRID": (-123.9, 46.1, -123.6, 46.3),
        "DBOFS": (-75.5, 38.5, -74.5, 39.25),
        "DBOFS-REGULARGRID": (-75.5, 38.5, -74.5, 39.25),
        "GFS-1-2DEG": (-85.0, 25.0, -60.0, 48.0),
        "GFS-1-4DEG": (-85.0, 25.0, -60.0, 48.0),
        "GFS-1DEG": (-85.0, 25.0, -60.0, 48.0),
        "GOMOFS": (-70, 41, -66, 44),
        "GOMOFS-2DS": (-70, 41, -66, 44),
        "GOMOFS-REGULARGRID": (-70, 41, -66, 44),
        "HYCOM": (-79.10, 31.84, -68.159, 42.29),
        "LEOFS": (-83.6, 41.5, -82.6, 42.1),
        "LEOFS-REGULARGRID": (-83.6, 41.5, -82.6, 42.1),
        "LMHOFS": (-88, 41.57, -86, 44),
        "LMHOFS-REGULARGRID": (-88, 41.57, -86, 44),
        "LOOFS": (-78.6, 43.4, -77.1, 43.7),
        "LSOFS": (-89.4, 47.0, -86.4, 47.75),
        "NGOFS2": (-91.5, 29.25, -91, 29.75),
        "NGOFS2-2DS": (-91.5, 29.25, -91, 29.75),
        "NGOFS2-REGULARGRID": (-91.5, 29.25, -91, 29.75),
        "NYOFS": (-74.1, 40.49, -73.95, 40.61),
        "SFBOFS": (-122.55, 37.75, -122.4, 37.9),
        "SFBOFS-REGULARGRID": (-122.55, 37.75, -122.4, 37.9),
        "TBOFS": (-82.9, 27.3, -82.6, 27.7),
        "TBOFS-REGULARGRID": (-82.9, 27.3, -82.6, 27.7),
        "WCOFS": (-122.0, 25.0, -115.0, 35.0),
        "WCOFS-2DS": (-122.0, 25.0, -115.0, 35.0),
        "WCOFS-REGULARGRID": (-122.0, 25.0, -115.0, 35.0),
    }

    return bboxes[model_id]


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
        raise ValueError(
            f"Invalid coordinate system. Options are: {COORDSYSTEMS}")
    if not (-180.0 <= lon <= 360.0):
        raise ValueError(
            f"longitude cannot be larger than 360 or less than -180. Got{lon}")

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
    interval_1 = [datetime.datetime.fromisoformat(x) for x in interval_1]
    interval_2 = [datetime.datetime.fromisoformat(x) for x in interval_2]
    if not check_valid_interval(interval_1):
        raise ValueError("Start is not before or equal to end for interval 1")
    if not check_valid_interval(interval_2):
        raise ValueError("Start is not before or equal to end for interval 2")
    return (interval_1[0] <= interval_2[1] and interval_1[1] >= interval_2[0])
    


def polygon2bbox(bounds):
    """
    converts four points to a four value tuple defining a bounding box.

    In the form: (min_lat, min_lon, max_lat, max_lon)
    """

    if len(bounds) < 2:
        raise ValueError("Bounding box requires at least 2 points")

    try:
        bounds = np.asarray(bounds, dtype=np.float64).reshape(-1, 2)
    except ValueError as err:
        raise ValueError("bounds must be pairs of (lon, lat) points") from err
    min_lon, min_lat = bounds.min(axis=0)
    max_lon, max_lat = bounds.max(axis=0)
    return ((min_lon, min_lat), (max_lon, max_lat))


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
        if ev_p not in ENVIRONMENTAL_PARAMETERS.keys():
            raise KeyError(
                "{} is not a valid environmental parameter".format(ev_p))
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
        bb[0] -= 360
        bb[2] -= 360
    bb_poly = MultiPoint([(bb[0], bb[1]), (bb[2], bb[3])]).envelope
    return bb_poly.intersects(poly_bounds)


def subset_intersects_model_boundary(model_bounds, poly_bounds):
    """
    :param model_bounds: model boundary from metadata
    :param poly_bounds: shapely Polygon (map) boundary.
           Coords must be in (-180, -90), (180, 90) range
    """
    poly_bounds = Polygon(poly_bounds)
    model_bounds = np.array(model_bounds)
    if np.any(model_bounds[:, 0] > 180):
        model_bounds[:, 0] = model_bounds[:, 0] - 360
    model_bounds_poly = Polygon(model_bounds)
    return model_bounds_poly.intersects(poly_bounds)


def filter_models(models_metadatas,
                  map_bounds=None,
                  model_ids_sources=None,
                  env_params=None):
    """
    Filters a provided list of model metadata via three criteria:
    1. Intersects with provided polygon boundary
    2. Model ids and source locations
    3. Present environmental parameters

    :param models_metadatas: list of model Metadata objects
    :param map_bounds: list of tuples (coordinates), or shapely Polygon, or None
    :param model_ids_sources: dict with keys as names of models and lists of sources
    :param env_params: string eg 'surface_currents' or list of string eg ['surface_currents', '3D_temperature']
        see libgoods.model.ENVIRONMENTAL_PARAMETERS for valid query strings
    """
    retlist = models_metadatas
    if model_ids_sources is not None:
        retlist = [
            m for m in retlist if m.identifier in model_ids_sources.keys()
        ]

        # we might want to make the sorting on source optional so we can return all w/o specifying
        for ii, m in enumerate(retlist):
            sources = m.sources
            keep_source_list = []
            for source in sources:
                if source.name in model_ids_sources[m.identifier]:
                    keep_source_list.append(source)
            retlist[ii].sources = keep_source_list

    if map_bounds is not None:
        map_bounds = (Polygon(map_bounds)
                      if not isinstance(map_bounds, Polygon) else map_bounds)
        retlist = [
            m for m in retlist if _filter_by_bb_intersection(m, map_bounds)
        ]

    if env_params is not None:
        retlist = [m for m in retlist if _filter_by_env_params(m, env_params)]

    return retlist


def file2dt(filename):
    """!!!!Copied from model_catalogs for convenience
    Return Timestamp of NOAA OFS filename
    ...without reading in the filename to xarray. See `docs <https://model-catalogs.readthedocs.io/en/latest/aggregations.html>`_ for details on the formula. Most NOAA OFS models have 1 timestep per file, but NYOFS has 6.

    Parameters
    ----------
    filename : str
        Filename for which to decipher datetime. Can be full path or just file name.

    Returns
    -------
    Timestamp
        datetime of the time(s) in the file.

    Examples
    --------
    >>> url = 'https://www.ncei.noaa.gov/thredds/dodsC/model-cbofs-files/2022/07/nos.cbofs.fields.n001.20220701.t00z.nc'
    >>> mc.filename2datetime(url)
    Timestamp('2022-06-30 19:00:00')
    """

    # strip off path if present since can mess up the matching
    filename = filename.split("/")[-1]

    # read in date from filename
    date = pd.to_datetime(filename, format="%Y%m%d",
                          exact=False)  # has time 00:00

    # pull timing cycle from filename
    regex = re.compile(".t[0-9]{2}z.")
    cycle = int(regex.findall(filename)[0][2:4])

    # NYOFS: multiple times per file
    if fnmatch.fnmatch(filename, "*.nowcast.*"):

        date = [
            date + pd.Timedelta(f"{cycle - dt} hours") for dt in range(6)[::-1]
        ]

    # NYOFS: multiple times per file
    elif fnmatch.fnmatch(filename, "*.forecast.*"):

        # models all have different forecast lengths! Though only nyofs is left in this category
        if "nyofs" in filename:
            nfiles = 54

        date = [
            date + pd.Timedelta(f"{cycle + 1 + dt} hours")
            for dt in range(nfiles)
        ]

    # Main style of NOAA OFS files, 1 file per time step
    elif fnmatch.fnmatch(filename, "*.n???.*") or fnmatch.fnmatch(
            filename, "*.f???.*"):

        # number of hours in repeat cycle for forecast
        if "wcofs" in filename:
            tshift = 24
        else:
            tshift = 6

        # pull hours from filename
        regex = re.compile(".[n,f][0-9]{3}.")
        hour = int(regex.findall(filename)[0][2:-1])

        # calculate hours
        dt = cycle + hour

        # if nowcast file, subtract dt hours
        if fnmatch.fnmatch(filename, "*.n???.*"):
            dt -= tshift

        # construct datetime. dt might be negative.
        date += pd.Timedelta(f"{dt} hours")

    return date.to_pydatetime()


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
    """

    dt += datetime.timedelta(seconds=30)
    return dt.replace(microsecond=0).replace(second=0)
