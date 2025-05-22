"""
A class for dealing with regular grid model output and converting to GNOME format
By passing in a var_map dict the
variable names can be customized for different models or datasets
"""

import numpy as np
from netCDF4 import Dataset, MFDataset

from . import base


class rect(base.nc):
    """
    A class for dealing with regular grid model output and converting to GNOME format
    By passing in a var_map dict the
    variable names can be customized for different models or datasets
    """

    def get_dimensions(self, var_map, get_time=True, get_xy=True, get_z=False):
        """get dimensions for roms models"""
        if get_time:
            self.time_varname = var_map["time"]
            self.time = self.Dataset.variables[var_map["time"]][:]
            self.time_units = self.Dataset[var_map["time"]].units
            self.time_dimension = self.Dataset.variables[var_map["time"]].dimensions

        if get_xy:
            if self.GridDataset is not None:
                ds = self.GridDataset
            else:
                ds = self.Dataset
            self.lon = ds.variables[var_map["longitude"]][:]
            self.lat = ds.variables[var_map["latitude"]][:]
            self.lon_dimension = ds.variables[var_map["longitude"]].dimensions
            self.lat_dimension = ds.variables[var_map["latitude"]].dimensions
            self.x = [0, len(self.lon), 1]
            self.y = [0, len(self.lat), 1]

            # self.lon = (self.lon > 180).choose(self.lon, self.lon - 360)

        if get_z:
            self.depth = ds.variables[var_map["z"]][:]
            self.depth_dimension = ds.variables[var_map["z"]].dimensions
            self.z = [0, self.depth.shape[0]]

    def subset(self, bbox, stride=1, dl=False):
        """
        bbox = [wlon,slat,elon,nlat]

        """
        subset_lat = np.nonzero(np.logical_and(self.lat >= bbox[1], self.lat <= bbox[3]))[0]

        if not dl:
            subset_lon = np.nonzero(np.logical_and(self.lon >= bbox[0], self.lon <= bbox[2]))[0]
        else:
            subset_lon = np.nonzero(np.logical_and(self.lon >= bbox[0], self.lon <= bbox[2] + 360))[
                0
            ]

        if stride >= len(subset_lat):
            stride = 1

        self.y = [subset_lat[0], subset_lat[-1] + 1, stride]
        self.x = [subset_lon[0], subset_lon[-1] + 1, stride]

    def write_nc(  # noqa: C901
        self,
        var_map,
        ofn="test.nc",
        t_index=None,
        d_index=0,
        is3d=False,
        grid_only=False,
        dl=False,
    ):
        """
        Write a rectangular grid model file
        Note: some of these input params aren't used at present; trying to have same params as other grid types
        """
        nc_in = self.Dataset
        nc_in.set_auto_maskandscale(False)

        if self.GridDataset is not None:
            nc_grid = self.GridDataset
            nc_grid.set_auto_maskandscale(False)
        else:
            nc_grid = nc_in

        nc_out = Dataset(ofn, "w", format="NETCDF3_CLASSIC")

        if not grid_only:
            if t_index is not None:
                self.time = self.time[t_index[0] : t_index[1] : t_index[2]]
            else:
                t_index = [0, len(self.time), 1]
            nc_out.createDimension(self.time_dimension[0], None)
            tvar = nc_out.createVariable(self.time_varname, "f4", self.time_dimension)
            tvar[:] = self.time[:]
            tvar.setncattr("units", self.time_units)

        nc_out.createDimension(self.lat_dimension[0], self.y[1] - self.y[0])
        nc_out.createDimension(self.lon_dimension[0], self.x[1] - self.x[0])

        var_in = nc_grid.variables[var_map["longitude"]]
        var_out = nc_out.createVariable(var_map["longitude"], var_in.dtype, self.lon_dimension)
        lon = var_in[self.x[0] : self.x[1] : self.x[2]]
        if dl is False:
            var_out[:] = (lon > 180).choose(lon, lon - 360)  # -180-->180
        else:
            var_out[:] = (lon < 0).choose(lon, lon + 360)  # 0-->360
        # Copy NetCDF attributes:
        for attr in var_in.ncattrs():
            var_out.setncattr(attr, var_in.getncattr(attr))

        var_in = nc_grid.variables[var_map["latitude"]]
        var_out = nc_out.createVariable(var_map["latitude"], var_in.dtype, self.lat_dimension)
        var_out[:] = var_in[self.y[0] : self.y[1] : self.y[2]]
        # Copy NetCDF attributes:
        for attr in var_in.ncattrs():
            var_out.setncattr(attr, var_in.getncattr(attr))

        if "mask" in var_map:
            var_in = nc_in.variables[var_map["mask"]]
            dims = (var_in.dimensions[-2], var_in.dimensions[-1])
            var_out = nc_out.createVariable("mask", var_in.dtype, dims)
            var_out[:] = var_in[
                self.y[0] : self.y[1] : self.y[2], self.x[0] : self.x[1] : self.x[2]
            ]
            # Copy NetCDF attributes:
            for attr in var_in.ncattrs():
                var_out.setncattr(attr, var_in.getncattr(attr))

        if is3d:  # this only works with level depths (all I have seen so far)
            nc_out.createDimension(self.depth_dimension[0], self.z[1])
            var_in = nc_in.variables[var_map["z"]]
            dims = var_in.dimensions[0]
            var_out = nc_out.createVariable("depth", var_in.dtype, dims)
            var_out[:] = var_in[:]
            # Copy NetCDF attributes:
            for attr in var_in.ncattrs():
                var_out.setncattr(attr, var_in.getncattr(attr))

        if not grid_only:
            # determine which data is desired from var_map
            data_vars = []
            for var in self.data_vars:
                if var in var_map:
                    data_vars.append(var_map[var])

            for var in data_vars:
                var_in = nc_in.variables[var]
                # Create variable in new file
                if is3d:
                    dims = (
                        self.time_dimension[0],
                        self.depth_dimension[0],
                        var_in.dimensions[-2],
                        var_in.dimensions[-1],
                    )
                else:
                    dims = (
                        self.time_dimension[0],
                        var_in.dimensions[-2],
                        var_in.dimensions[-1],
                    )
                var_out = nc_out.createVariable(var, var_in.dtype, dims)
                # Copy data:
                if len(var_in.shape) == 4:
                    if is3d:
                        var_out[:] = var_in[
                            t_index[0] : t_index[1] : t_index[2],
                            :,
                            self.y[0] : self.y[1],
                            self.x[0] : self.x[1],
                        ]
                    else:
                        var_out[:] = var_in[
                            t_index[0] : t_index[1] : t_index[2],
                            d_index,
                            self.y[0] : self.y[1],
                            self.x[0] : self.x[1],
                        ]
                elif len(var_in.shape) == 3:
                    var_out[:] = var_in[
                        t_index[0] : t_index[1] : t_index[2],
                        self.y[0] : self.y[1],
                        self.x[0] : self.x[1],
                    ]

                # Copy NetCDF attributes:
                if type(self.Dataset) is MFDataset:
                    var_in = Dataset(self.FileName[0]).variables[var]
                for attr in var_in.ncattrs():
                    if attr != "_FillValue":
                        var_out.setncattr(attr, var_in.getncattr(attr))

                if not hasattr(var_out, "missing_value"):  # need to check for nans
                    if np.isnan(var_out).any():
                        var_out.setncattr("missing_value", np.nan)

                # check for nans - replace with zero
                var_out[:] = np.nan_to_num(var_out)

        nc_out.close()
