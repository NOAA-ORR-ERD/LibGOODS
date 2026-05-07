"""
Code for extracting shoreline files

Currently supports GSHHS and (older) NOS shoreline

NOTE: for Open Street Map, see some example code in the example_scripts dir
in this project
"""

from pathlib import Path

import fiona
import numpy as np
import shapely.geometry as sgeo

from libgoods import config

# shoreline_dir = Path(__file__).parent / "shoreline_data"

# this dict maps shoreline dataset options to subdirectories where shapefiles can be
# found (the "nos" and "gshhs" keys match what is curently coming from WebGNOME client

shoreline_datasets = {
    "AK_CUSP": ["AK_CUSP", "AK_CUSP_polygon_20240221.shp"],
    "NE_CUSP": ["ME_to_DE_CUSP", "ME_NH_MA_CT_RI_VT_NY_NJ_DE_20241009.shp"],
    "nos": ["nos_shoreline", "nosshore.shp"],
    "OSM": ["OpenStreetMap", "land-polygons-complete-4326", "land_polygons.shp"],
    "gshhs": ["gshhg", "GSHHS_shp"],
    "GI": ["ERMA", "Coastal_Land_Area.shp"]
}
# call this in one place:
# opens up the option of having different datasets in different places.
shoreline_datasets = {name: config.shoreline_dir.joinpath(*paths)
                      for name, paths in shoreline_datasets.items()}


def format_for_bna(filename, polys, levs, dl=False):
    data = []
    ii = 1
    for lev, poly in zip(levs, polys):
        x = np.array(poly[0])
        y = np.array(poly[1])
        if dl:
            x = (x < 0).choose(x, x + 360)
        if lev == 0:
            data.append('"Map Bounds", "2", ' + str(len(x)))
        else:
            data.append('"' + str(ii) + '","' + str(int(lev)) + '",' + str(len(x)))
        for lon, lat in zip(x, y):
            data.append(f"{lon:.6f}" + ", " + f"{lat:.6f}")
        ii = ii + 1
    data = "\n".join(data)
    with open(filename, "w") as outfile:
        outfile.write(data)


def load_polys_and_clip(shpfile, bound_box, dl=False, lev=1, skip_errors=False):
    """
    Loop through polygons in shapefile, if they overlap with user
    specified rectangle, load the polygon and clip

    Note that GSHHS polygons are -180-->180,so shorelines that cross the 180 line are
    clipped into west and east polygons, so there is some special casing to handle
    clip rectangles that cross the dateline
    Change lev to 2 if loading lakes

    These *may not* be able to be used to clip trajectories from GAn in Arc?

    :param bound_box: bounding box in the form: (min_lon, min_lat, max_lon, max_lat)

    :param shfile: path to a shapefile of land polygons

    :param dl=False: ???

    :param lev=1: topological level -- 1 == land 2 == lake in land, ...
                  this matches what the GSHHS does anyway

    """

    wl, sl, el, nl = bound_box

    if dl:
        bound_box = (-180, sl, 180, nl)

    clip_box = sgeo.box(*bound_box)

    bna_polys = []

    with fiona.open(shpfile) as source:
        for idx1, s in enumerate(source.filter(bbox=bound_box)):
            geo = s["geometry"]["coordinates"]
            for idx2, c in enumerate(geo):
                poly = sgeo.Polygon(c)
                if dl:
                    poly_bnds = poly.bounds
                    if poly_bnds[0] > -10 and poly_bnds[2] <= 180:
                        clip_box = sgeo.box(wl, sl, 180, nl)
                    else:
                        clip_box = sgeo.box(-180, sl, el, nl)
                if poly.intersects(clip_box):
                    try:
                        clipped_polys = poly.intersection(clip_box)
                    except Exception: # shapely.GEOSException:
                        if skip_errors:
                            print(f"Error: skipping polygon: {idx1}:{idx2}")
                        else:
                            raise
                    if type(clipped_polys) is sgeo.multipolygon.MultiPolygon:
                        for clipped_poly in clipped_polys.geoms:
                            try:
                                bna_polys.append(clipped_poly.exterior.xy)
                            except AttributeError:
                                pass
                    elif type(clipped_polys) is sgeo.polygon.Polygon:
                        try:
                            bna_polys.append(clipped_polys.exterior.xy)
                        except AttributeError:
                            pass
                else:
                    continue

    if len(bna_polys) < 1 and lev == 1:  # all water
        bna_polys.append(clip_box.exterior.xy)
        levels = [
            2,
        ]
    else:  # define levels and add lakes if specified
        levels = [lev for x in range(len(bna_polys))]

    # add the map bounds
    # level 0 is map bounds
    if lev == 1:
        bna_polys.insert(0, ([wl, wl, el, el], [sl, nl, nl, sl]))
        levels.insert(0, 0)

    return bna_polys, levels


def get_map(
    bounds,
    data_source="gshhs",
    ofn="coast.bna",
    resolution="h",
    cross_dateline=False,
    max_filesize=1e6,
    include_lakes=True,
    skip_errors=False
):
    """
    Parameters
    ----------
        bounds: tuple
            (lon_min, lat_min, lon_max, lat_max)
        data_source: str
            which data to use: options include:
            "gshhs", "nos" -- others are experimental.

            For full list: `shoreline.shoreline_datasets.keys()`

            To point to custom dataset, pass in a path to a shapefile.

        resolution: str default: "f"
            for GSHHS - one of "c", "i", "h", "f" (coarse, intermediate, high, full)

        include_lakes: bool
            only valid for GSHHS dataset where lakes are in separate shapefile

        skip_errors: bool default: False. If True, a polygon will be skipped if
            an error is raised trying to clip it.
    """
    bbox = bounds
    try:
        shapefile_path = shoreline_datasets[data_source]
    except KeyError:
        shapefile_path = Path(data_source)
        if not shapefile_path.is_file():
            raise ValueError(f'"{data_source}" is not a valid shoreline '
                             'dataset and {shapefile_path} is not a file.')

    if data_source == "gshhs":
        # extra stuff to find the nested dirs for the resolution
        fname = "GSHHS_" + resolution + "_L1.shp"
        shpfile = shapefile_path.joinpath(resolution, fname)
        bna_polys, levs = load_polys_and_clip(shpfile,
                                              bbox,
                                              dl=cross_dateline,
                                              skip_errors=skip_errors)
        if include_lakes:
            # "L2" which is lakes (L3/4 gets down to ponds in islands in lakes
            # and L5/6 are for Antarctica
            fname = "GSHHS_" + resolution + "_L2.shp"
            shpfile = shapefile_path.joinpath(resolution, fname)
            bna_polys2, levs2 = load_polys_and_clip(shpfile,
                                                    bbox,
                                                    dl=cross_dateline,
                                                    lev=2,
                                                    skip_errors=skip_errors)
            bna_polys.extend(bna_polys2)
            levs.extend(levs2)
    else:
        bna_polys, levs = load_polys_and_clip(shapefile_path,
                                              bbox,
                                              dl=cross_dateline,
                                              skip_errors=skip_errors)

    format_for_bna(ofn, bna_polys, levs, dl=cross_dateline)
