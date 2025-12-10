#!/usr/bin/env python
"""
A module that contains various functions for reading and writing
and checking GNOME shoreline files.

Currently only support BNA, but maybe others in the future?
"""

import os

import numpy as np


class GNOME_shoreline:
    """
    class to hold GNOME shoreline data
    """
    def __init__(self, filename=None):
        if filename is not None:
            self.read_bna(filename)
        else:
            self._init_lists()

    def _init_lists(self):
        self.map_bounds = []
        self.spillable_area = []
        self.lake_polys = []
        self.land_polys = []
        self.other_polys = []

    def _get_next_bna_polygon(self, fp):
        """
        Utility function that returns the next polygon from a BNA file

        returns: (points, poly_type, name, sname) where:
            points:    Nx2numpy array of floats with the points
            poly_type: one of "point", "line", "polygon"
            name:      name defined in the BNA
            sname:     secondary name defined in the BNA

            "holes" in polygons are not supported in this code.
        See:
           http://www.softwright.com/faq/support/boundary_file_bna_format.html

        NOTE: This code doesn't allow extra spaces around the commas in the
              header line.
              If there are no commas allowed in the name, it would be easier to
              simply split on the commas
              (or march through the line looking for the quotes -- regex?)
        """
        while True:  # skip blank lines
            header = fp.readline()
            if not header:  # end of file
                return None
            if header.strip():  # found a header
                break
            else:
                continue

        try:
            fields = header.split('"')
            name = fields[1]
            sname = fields[3]
            num_points = int(fields[4].strip()[1:])
        except (ValueError, IndexError):
            raise ValueError(f"File has incorrect header for BNA format: {header}")

        # if num_points < 0 or num_points == 2:
        #     raise ValueError("GNOME Map BNA doesnot support polylines")
        #     # poly_type = "polyline"
        #     # num_points = abs(num_points)
        # elif num_points == 1:
        #     poly_type = "point"
        if num_points <= 2:
            raise ValueError(f"polygon {name} does not have a valid number of points: {num_points}.")

        points = np.zeros((num_points, 2), dtype=np.float64)
        for i in range(num_points):
            line = fp.readline()
            if not line:
                raise ValueError(f"empty coords line in {header.strip()}. check number of vertices")
            try:
                points[i, :] = [float(j) for j in line.split(",")]
            except ValueError as err:
                raise ValueError(f"incorrect coords in line: {line} in poly: {header}") from err
        return (points, name, sname)


    def write_bna(self, filename):
        """
        Writes a BNA file to filename

        :param filename: A filename to write to.
        """
        outfile = open(filename, "w")

        polyset = (self.map_bounds
                   + self.spillable_area
                   + self.land_polys
                   + self.lake_polys
                   + self.other_polys)

        for poly in polyset:
            verts = poly[0]
            outfile.write(f'"{poly[1]}", "{poly[2]}", {len(verts)}\n')
            for point in verts:
                # point = np.asarray(point)
                outfile.write(f"{point[0]:.8f}, {point[1]:.8f} \n")

    def read_bna(self, filename):
        """
        Read a bna file.

        :param filename: A filename to read from
        """
        self._init_lists()

        with open(filename, encoding='utf-8') as fd:
            polys = []

            while True:
                poly = self._get_next_bna_polygon(fd)

                if poly is None:
                    break
                if "".join(poly[1].split()).strip().lower() == "mapbounds":
                    self.map_bounds.append(poly)
                elif "".join(poly[1].split()).strip().lower() == "spillablearea":
                    self.spillable_area.append(poly)
                else:
                    if poly[2] == "1":
                        self.land_polys.append(poly)
                    elif poly[2] == "2":
                        self.lake_polys.append(poly)
                    else:
                        self.other_polys.append(poly)
        return None

    def __str__(self):
        return (f"GNOME_shoreline:\n"
                f"{len(self.map_bounds)} Map Bounds polygons\n"
                f"{len(self.spillable_area)} Spillable Area polygons\n"
                f"{len(self.land_polys)} Land polygons\n"
                f"{len(self.other_polys)} Other polygons\n"
                )
    def is_similar(self, other):
        """
        returns true if the two shorelines are similar (maybe the same):

        same number of polygons of each type, etc.
        """
        if (len(self.map_bounds) == len(other.map_bounds)
            and len(self.spillable_area) == len(other.spillable_area)
            and len(self.lake_polys) == len(other.lake_polys)
            and len(self.land_polys) == len(other.land_polys)
            and len(self.other_polys) == len(other.other_polys)
            ):
            return True
        else:
            return False
