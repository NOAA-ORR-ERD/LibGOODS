#!/usr/bin/env python
import numpy as np
from netCDF4 import Dataset, MFDataset
from libgoods import base

class curv(base.nc):
         
    def get_dimensions(self,var_map,get_time=True,get_xy=True,get_z=False):
        '''
        Get the model dimensions (time,x,y)
        Can get just time dimension, just xy, or everything
        '''
        
        if get_time:
            self.time_varname = var_map['time']
            self.time = self.Dataset.variables[var_map['time']][:]
            self.time_units = self.Dataset[var_map['time']].units
            self.time_dimension = self.Dataset.variables[var_map['time']].dimensions
        
        if get_xy:
            if self.GridDataset is not None:
                self.lon = self.GridDataset.variables[var_map['lon']][:]
                self.lat = self.GridDataset.variables[var_map['lat']][:]
            else:
                self.lon = self.Dataset.variables[var_map['lon']][:]
                self.lat = self.Dataset.variables[var_map['lat']][:]
            
            self.x = [0,self.lon.shape[1]]
            self.y = [0,self.lat.shape[0]]
            self.lon = (self.lon > 180).choose(self.lon,self.lon-360)
            
        if get_z:
            self.depth = self.Dataset.variables[var_map['z']]
            self.z = [0,self.depth.shape[0]]
            
           
    def subset(self,bbox,stride=1,dl=True):
        '''
        bbox = [slat,wlon,nlat,elon]
   
        '''
        glat = self.lat
        glon = self.lon
        
        sl = bbox[0]
        nl = bbox[2]
        wl = bbox[1]
        el = bbox[3]
        
        if (abs(np.nanmax(glat)-nl) < 1e-3) and (abs(np.nanmin(glon)-wl) < 1e-3): #original values
            self.y = [0,np.size(glat,0),1]
            self.x = [0,np.size(glat,1),1]
        else: #do subset
                     
            if not dl:
                [yvec,xvec] = np.where(np.logical_and(np.logical_and(glat>=sl,glat<=nl),np.logical_and(glon>=wl,glon<=el)))
            else:
                [yvec,xvec] = np.where(np.logical_and(np.logical_and(glat>=sl,glat<=nl),np.logical_or(glon>=wl,glon<=el)))
                #self.dlx = 1 #Could do this to make the writing not need the dl flag passed in explicity
                
            if len(yvec) > 2 and len(xvec) > 2:
                y1 = min(yvec)
                y2 = max(yvec)+1
                x1 = min(xvec)
                x2 = max(xvec)+1
                self.y = [y1,y2,stride]
                self.x = [x1,x2,stride]           
            else:
                self.y = [0,np.size(glat,0),1]
                self.x = [0,np.size(glat,1),1]
               
        
 
        


    
