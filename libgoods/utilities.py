"""
assorted utilities useful for libgoods
"""
import numpy as np
from shapely.geometry import Polygon, MultiPoint

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
        raise ValueError(
            f"longitude cannot be larger than 360 or less than -180. Got{lon}"
        )

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
        if ev_p not in ENVIRONMENTAL_PARAMETERS.keys():
            raise KeyError("{} is not a valid environmental parameter".format(ev_p))
        return ev_p in mdl_meta.env_params
    else:
        # assume multiple filter parameters eg ['surface currents', 'surface winds']
        return all([param in mdl_meta.env_params for param in ev_p])


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


def filter_models(models_metadatas, map_bounds=None, model_ids_sources=None, env_params=None):
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
        retlist = [m for m in retlist if m.identifier in model_ids_sources.keys()]
        
        #we might want to make the sorting on source optional so we can return all w/o specifying
        for ii,m in enumerate(retlist):
            sources = m.sources
            keep_source_list = []
            for source in sources:
                if source.name in model_ids_sources[m.identifier]:
                    keep_source_list.append(source)
            retlist[ii].sources = keep_source_list
            

    if map_bounds is not None:
        map_bounds = (
            Polygon(map_bounds) if not isinstance(map_bounds, Polygon) else map_bounds
        )
        retlist = [m for m in retlist if _filter_by_bb_intersection(m, map_bounds)]

    if env_params is not None:
        retlist = [m for m in retlist if _filter_by_env_params(m, env_params)]

    return retlist
    
