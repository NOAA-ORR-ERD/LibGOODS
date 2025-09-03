"""
Base model class
"""

import datetime
from netCDF4 import Dataset, MFDataset, num2date
from libgoods import standard_names

class BaseModel():
    """
    Base model class
    """

    # This should be the master list of variables we might want to retreive.
    # Individual model var_maps will map to these names
    data_vars = standard_names.standard_names

    def open_nc(self, FileName=None, GridFileName=None, tvar=None):
        """
        Load from OpenDAP URL or local netCDF file
        Option for using separate grid file
        If tvar is not none, add formatted start/end date
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

        if tvar is not None:
            t = self.Dataset.variables[tvar]
            self.start_date = num2date(t[0], t.units).strftime()
            self.end_date = num2date(t[-1], t.units).strftime()


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

        Buffer_hrs - adds a default 6 hour buffer to start and end times
        since model timestep may not align with chosen start/end time
        """
        dts = num2date(self.time, self.time_units)
        if not isinstance(start, datetime.datetime):
            start = datetime.datetime.strptime(start, fmt)
        if not isinstance(end, datetime.datetime):
            end = datetime.datetime.strptime(end, fmt)

        t1 = [i for i, dt in enumerate(dts) if dt <= start]
        if len(t1) == 0:
            t1 = 0  # all time values are > than start time
        elif len(t1) == len(dts):
            raise ValueError("Specified start time is later than model end time")
        else:
            t1 = t1[-1]

        t2 = [i for i, dt in enumerate(dts) if dt > end]
        if len(t2) == 0:
            t2 = len(dts) - 1  # all time values < end time
        elif len(t2) == len(dts):
            raise ValueError("Specified end time is before the model start time")
        else:
            t2 = t2[0] + 1

        return [t1, t2, 1]
