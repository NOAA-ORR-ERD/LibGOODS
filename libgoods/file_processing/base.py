"""
Base model class
"""
#!/usr/bin/env python
from __future__ import print_function
import numpy as np
from netCDF4 import Dataset, MFDataset, num2date
from libgoods import temp_files_dir
from ..utilities import polygon2bbox, flatten_bbox
import datetime
import os


class nc:
    """
    Base model class
    """

    # This should be the master list of variables we might want to retreive.
    # Individual model var_maps will map to these names
    data_vars = ["u", "v", "ice_u", "ice_v", "ice_thickness", "ice_fraction"]

    def open_nc(self, FileName=None, GridFileName=None):
        """
        Load from OpenDAP URL or local netCDF file
        """
        if FileName is not None:
            self.FileName = FileName
            if isinstance(FileName, list):
                self.Dataset = MFDataset(FileName)
            else:
                self.Dataset = Dataset(FileName)
        else:
            self.Dataset = None

        if GridFileName is not None:
            self.GridFileName = GridFileName
            self.GridDataset = Dataset(GridFileName)
        else:
            self.GridDataset = None

    def get_data(self, bounds, cross_dateline, max_filesize, target_dir=None):

        """
        NOTE: This "does it all" -- i.e. it assumes you are already happy with the subset selection
        box -- often we want to check the size of a subset before we do the download

        :param: bounds Sequence of (lon,lat) pairs e.g., [(lon,lat),(lon,lat)...]
        """
        try:
            bounding_box = flatten_bbox(polygon2bbox(bounds))
        except ValueError:
            raise NotImplementedError("Only rectangular bounds are supported")

        # bounds = [south_lat,west_lon,north_lat,east_lon]
        url = self.url
        var_map = self.var_map

        self.get_dimensions(var_map)
        self.subset(bounding_box)

        # until I add time selection this will get a reasonal time slice for latest TBOFS/HYCOM
        tlen = len(self.time)
        if self.metadata.identifier == "TBOFS":
            t_index = [tlen - 72, tlen, 1]
        else:
            t_index = [40, 70, 1]

        fn = self.default_filename
        if target_dir is None:
            target_dir = temp_files_dir
        fp = os.path.join(target_dir, fn)
        self.write_nc(var_map, fp, t_index=t_index)

        return fp

    def update(self, FileName):
        """
        Change nc Dataset to point to a new nc file or url without reinitializing everything (retain grid info)
        """
        if isinstance(FileName, list):
            self.Dataset = MFDataset(FileName)
        else:
            self.Dataset = Dataset(FileName)

    def when(self):
        """
        Gives some info about the time dimension but only AFTER get_dimensions has been called
        """
        sd = num2date(self.time[0], self.time_units)
        ed = num2date(self.time[-1], self.time_units)
        if len(self.time) > 1:
            dt = self.time[1] - self.time[0]
        else:
            dt = None
        print("Start date: ", sd)
        print("End date: ", ed)
        print("Time step: ", dt, "in units of", self.time_units)
        print("Length:", len(self.time))

    def get_timeslice_indices(self, start, end, fmt="%Y-%m-%dT%H:%M:%S"):
        """
        Start/end are strings in format %Y-%m-%dT%H:%M:%S
        or datetimes
        """
        dts = num2date(self.time,self.time_units)
        if not isinstance(start, datetime.datetime):
            start = datetime.datetime.strptime(start,fmt)
        if not isinstance(end, datetime.datetime):
            end = datetime.datetime.strptime(end,fmt)
        t1 = [i for i,dt in enumerate(dts) if dt>=start][0]
        t2 = [i for i,dt in enumerate(dts) if dt<=end][-1] + 1
        
        return t1,t2

