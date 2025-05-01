# a quick check of subsettting OSM land polygons

"""
This is a quick demo of subsetting the OSM shorelines to get a GNOME BNA map

DATA downloaded from:

https://osmdata.openstreetmap.de/data/land-polygons.html


NOTES:

Total of 785135 polygons

Takes a long time to run through them all linearly.
"""



import fiona
from shapely.geometry import shape
from shapely import  box

# Near Seattle: Elliot Bay

# a bigger one:
UR = (-122.2, 47.7)
LL = (-122.6, 47.5)

OSM_file = 'land-polygons-complete-4326/land_polygons.shp'

outfilename = "ElliotBay.bna"

# This makes a polygon from the bounds
# It can also be a polygon -- does not have to be a rect.
bounds = box(*(LL + UR))

def get_stats():
    """
    utility to get a bit on info about the data -- not really needed anymore.
    """
    stats = {}
    with fiona.open(OSM_file, 'r') as land_polys:
        print(len(land_polys))
        for i, feat in enumerate(land_polys):
            gtype = str(feat.geometry.type)
            num_rings = len(feat.geometry.coordinates)
            f_stat = stats.setdefault(gtype, {})
            num_feats = f_stat.setdefault(num_rings, 0)
            f_stat[num_rings] += num_rings
            print(f"feature: {i} is a {gtype} with {num_rings} rings")

    return stats

def extract_some(end):
    """
    pulls a few polygons out of the pile, and saves them as a shapefile
    """
    with fiona.open(OSM_file, 'r') as source:

        # **source.meta is a shortcut to get the crs, driver, and schema
        # keyword arguments from the source Collection.
        with fiona.open(f'subset_of_{end}_polys.shp', 'w',
                        **source.meta) as sink:

            for i, f in enumerate(source):
                try:
                    geom = shape(f['geometry'])
                    if not geom.is_valid:
                        clean = geom.buffer(0.0)
                        assert clean.is_valid
                        assert clean.geom_type == 'Polygon'
                        geom = clean
                    # _dict = mapping(geom)
                    #f['geometry'] = mapping(geom)
                    sink.write(f)
                except Exception:
                    # Writing uncleanable features to a different shapefile
                    # is another option.
                    logging.exception("Error cleaning feature %s:", f['id'])
                if i >= end:
                    break

def write_ring(bna_file, coords, level=1):
    num_points = len(coords)
    bna_file.write(f'"{i}", "{level}", {num_points:d}\n') # "3","1",7
    for point in coords:
        bna_file.write(f'{point[0]:.12f}, {point[1]:.12f}\n')

def write_poly(bna_file, sub_poly):
    """
    writes a polygon to a BNA file.
    """
    write_ring(bna_file, sub_poly.exterior.coords)


with fiona.open(OSM_file, 'r') as source, open(outfilename, 'wt') as bna_file:
    num_polys = 0
    for i, f in enumerate(source):
    # for i, f in [(87719, source[87719])]:
        print(f"processing: {i}")
        poly = shape(f['geometry'])
        sub_poly = poly.intersection(bounds)
        if sub_poly.is_empty:
            continue
        print(f"found one: feature ID: {f.id}")
        if sub_poly.geom_type == 'MultiPolygon':
            for p in sub_poly.geoms:
                if p.interiors:
                    break
                num_polys += 1
                write_poly(bna_file, p)
        elif sub_poly.geom_type == 'Polygon':
            num_polys += 1
            write_poly(bna_file, sub_poly)

        else:
            print("Feature: {i} not a Polygon or MultiPolygon")

print(f"added: {num_polys} to BNA")


