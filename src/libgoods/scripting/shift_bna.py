"""
Script to shift the longitude of a BNA file to a different coordinate system

i.e. -180--180 or 0--360
"""

import sys

from libgoods.utilities import convert_longitude
from libgoods.utilities.haz_files import ReadBNA, WriteBNA

USAGE = """
shift_bna input_file coord_system

Convert longitude values in a BNA to a given coordinate system.

Options are:

"-180--180": Negative 180 degrees to 180 degrees

"0--360": Zero to 360 degrees
"""


def shift_bna(infilename, outfilename, coord_system):
    polys = ReadBNA(infilename)
    for poly in polys:
        poly[0][:, 0] = convert_longitude(poly[0][:, 0], coord_system=coord_system)

    WriteBNA(outfilename, polys)


def main():
    infilename = sys.argv[1]
    coord_system = sys.argv[2]

    outfilename = infilename.rsplit(".", 1)[0] + "_shifted.bna"

    shift_bna(infilename, outfilename, coord_system)


if __name__ == "__main__":
    main()
