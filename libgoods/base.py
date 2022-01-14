#!/usr/bin/env python
from __future__ import print_function
import numpy as np
from netCDF4 import Dataset, MFDataset, num2date

class nc():
    
    def __init__(self,FileName=None,GridFileName=None):
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
        
        #This should be the master list of variables we might want to retreive. Individual model var_maps will map to these names
        self.data_vars = ['u',
                          'v',
                          'ice_u',
                          'ice_v',
                          'ice_thickness',
                          'ice_fraction']
                          
        self.dlx = 0 #default does not cross dateline
        
    def update(self,FileName):
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

     