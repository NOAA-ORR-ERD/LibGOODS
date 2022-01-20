#!/usr/bin/env python
from __future__ import print_function
import numpy as np
from netCDF4 import Dataset, MFDataset, num2date
from libgoods import temp_files_dir
from .utilities import polygon2bbox
import os

class nc():

    #This should be the master list of variables we might want to retreive. Individual model var_maps will map to these names
    data_vars = ['u',
                 'v',
                 'ice_u',
                 'ice_v',
                 'ice_thickness',
                 'ice_fraction']

    def open_nc(self,FileName=None,GridFileName=None):
        '''
        Load from OpenDAP URL or local netCDF file
        '''
        if FileName is not None:
            self.FileName = FileName
            if isinstance(FileName,list):
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

    def get_data(self,
                 bounds,
                 cross_dateline,
                 max_filesize):

        '''
        NOTE: This "does it all" -- i.e. it assumes you are already happy with the subset selection
        box -- often we want to check the size of a subset before we do the download

        :param: bounds Sequence of (lon,lat) pairs e.g., [(lon,lat),(lon,lat)...]
        '''
        try:
            bounding_box = polygon2bbox(bounds)
        except ValueError:
            raise NotImplementedError('Only rectangular bounds are supported')

        #bounds = [south_lat,west_lon,north_lat,east_lon]
        url = self.url
        var_map = self.var_map

        self.get_dimensions(var_map)
        self.subset(bounding_box)

        #until I add time selection -- return last 10 time steps
        tlen = len(self.time)

        fn = self.default_filename
        fp = os.path.join(temp_files_dir,fn)
        self.write_nc(var_map,fp,t_index=[tlen-10,tlen,1])

        return fp

    def update(self, FileName):
        '''
        Change nc Dataset to point to a new nc file or url without reinitializing everything (retain grid info)
        '''
        if isinstance(FileName,list):
            self.Dataset = MFDataset(FileName)
        else:
            self.Dataset = Dataset(FileName)

    def when(self):
        '''
        Gives some info about the time dimension but only AFTER get_dimensions has been called
        '''
        sd = num2date(self.time[0], self.time_units)
        ed = num2date(self.time[-1], self.time_units)
        if len(self.time)>1:
            dt = self.time[1] - self.time[0]
        else:
            dt = None
        print('Start date: ', sd)
        print('End date: ', ed)
        print('Time step: ', dt, 'in units of', self.time_units)
        print('Length:', len(self.time))

