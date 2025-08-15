import pandas as pd
import xarray as xr
from libgoods.file_processing import rect_model
from .base import BaseModel


class NC4BaseModel(BaseModel):

    def open_ds(self):

        self.model = rect_model.rect()
        self.model.open_nc(self.location)
        self.model.get_dimensions(self.standard_names)
        t = self.model.time_dts
        self.actual_start = pd.to_datetime(t[0])
        self.actual_end = pd.to_datetime(t[-1]).to_pydatetime(t[-1])
        self.model.Dataset = None

    def subset_time(self, start_time, end_time):
        # TODO: make this smarter to use > start and/or < end etc (one end is None)
        # We also need to add some padding for output timesteps > 1 hour
        self.tindex = self.model.get_timeslice_indices(start_time, end_time)

    def subset_grid(self, bbox):
        # TODO: Add check on bbox and ds longitude to see if they are
        #       using same convention (0-->360 vs -180-180)
        self.model.subset(bbox)

    def filter_variables(self, variable_list=None):
        # This one is for surface only models (used by HFradar and ESPC)
        # variable list default is based on surface u/v variable names
        pass

    def make_xr_dataset(self):
        self.ds = xr.Dataset() # This is needed for the nbytes check in webgnomeapi - have to figure out what to do here.


    def write_nc(self, ofn="test.nc", close_ds=True):
        self.model.update(self.location)
        self.model.write_nc(self.standard_names, ofn, t_index=self.tindex)
        if close_ds:
            self.model.Dataset.close()
