"""
A class for loading variables from ROMS model output on specified domain subsets that are
needed for GNOME
"""
# ruff: noqa

import numpy as np
from netCDF4 import Dataset, MFDataset  # noqa: F401

from . import curv_model


class roms(curv_model.curv):
    """
    A class for loading variables from ROMS model output on specified domain subsets that are
    needed for GNOME
    """

    def get_dimensions(self, var_map=None, get_time=True, get_xy=True, get_z=False):
        """get dimensions for roms models"""

        if var_map is None:
            tvar = "ocean_time"
        else:
            tvar = var_map["time"]

        if get_time:
            self.time_varname = tvar
            self.time = self.Dataset.variables[tvar][:]
            self.time_units = self.Dataset[tvar].units
            self.time_dimension = self.Dataset.variables[tvar].dimensions

        if get_xy:
            if self.GridDataset is not None:
                self.lon = self.GridDataset.variables["lon_rho"][:]
                self.lat = self.GridDataset.variables["lat_rho"][:]
            else:
                self.lon = self.Dataset.variables["lon_rho"][:]
                self.lat = self.Dataset.variables["lat_rho"][:]

            self.x = [0, self.lon.shape[1]]
            self.y = [0, self.lat.shape[0]]

    def get_bdry(self):

            blon = []
            blat = []
            blon.extend(self.lon[0,:])
            blon.extend(self.lon[:,-1])
            blon.extend(self.lon[-1,::-1])
            blon.extend(self.lon[::-1,0])
            blat.extend(self.lat[0,:])
            blat.extend(self.lat[:,-1])
            blat.extend(self.lat[-1,::-1])
            blat.extend(self.lat[::-1,0])

            return blon, blat

    def write_nc(  # noqa: C901
        self,
        var_map=None,
        ofn="test.nc",
        t_index=None,
        d_index=-1,
        get3d=False,
        grid_only=False,
        dl=False,
    ):
        """
        Write a ROMS model file
        Note: some of these input params aren't used at present; trying to have same params as other grid types

        """
        include_wind = False
        if var_map is not None:
            # allow some default variable name overriding
            if "eastward_wind" in var_map:
                include_wind = True
                uwind = var_map["eastward_wind"]
                vwind = var_map["northward_wind"]

        nc_in = self.Dataset
        # nc_in.set_auto_maskandscale(False)
        nc_in.set_auto_scale(False)
        if self.GridDataset is not None:
            nc_grid = self.GridDataset
            # nc_grid.set_auto_maskandscale(False)
            nc_grid.set_auto_scale(False)
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

        nc_out.createDimension("eta_rho", self.y[1] - self.y[0])
        nc_out.createDimension("xi_rho", self.x[1] - self.x[0])
        nc_out.createDimension("eta_psi", self.y[1] - self.y[0] - 1)
        nc_out.createDimension("xi_psi", self.x[1] - self.x[0] - 1)
        nc_out.createDimension("eta_u", self.y[1] - self.y[0])
        nc_out.createDimension("xi_u", self.x[1] - self.x[0] - 1)
        nc_out.createDimension("eta_v", self.y[1] - self.y[0] - 1)
        nc_out.createDimension("xi_v", self.x[1] - self.x[0])

        if get3d:
            nc_out.createDimension("s_rho", nc_grid.dimensions["s_rho"].size)

        # List of variables to copy (they have to be in nc_in...):
        grid_vars = [
            "lon_rho",
            "lat_rho",
            "mask_rho",
            "lon_psi",
            "lat_psi",
            "mask_psi",
            "lon_u",
            "lat_u",
            "mask_u",
            "lon_v",
            "lat_v",
            "mask_v",
            "angle",
        ]

        if get3d:
            grid_vars.extend(["hc", "Cs_r", "s_rho", "h"])

        for var in grid_vars:
            # Create variable in new file:
            try:
                var_in = nc_grid.variables[var]
            except KeyError:
                print(var_in, " not found")
            try:
                dim1 = var_in.dimensions[0]
            except IndexError:
                var_out = nc_out.createVariable(var, var_in.dtype, ())
                var_out[:] = var_in[:]
            else:
                if dim1.find("s_rho") >= 0:
                    var_out = nc_out.createVariable(var, var_in.dtype, ("s_rho"))
                    # Copy data:
                    var_out[:] = var_in[:]
                elif dim1.find("_rho") >= 0:
                    var_out = nc_out.createVariable(var, var_in.dtype, ("eta_rho", "xi_rho"))
                    # Copy data:
                    var_out[:] = var_in[self.y[0] : self.y[1], self.x[0] : self.x[1]]
                elif dim1.find("_psi") >= 0:
                    var_out = nc_out.createVariable(var, var_in.dtype, ("eta_psi", "xi_psi"))
                    # Copy data:
                    var_out[:] = var_in[self.y[0] : self.y[1] - 1, self.x[0] : self.x[1] - 1]
                elif dim1.find("_u") >= 0:
                    var_out = nc_out.createVariable(var, var_in.dtype, ("eta_u", "xi_u"))
                    # Copy data:
                    var_out[:] = var_in[self.y[0] : self.y[1], self.x[0] : self.x[1] - 1]
                elif dim1.find("_v") >= 0:
                    var_out = nc_out.createVariable(var, var_in.dtype, ("eta_v", "xi_v"))
                    # Copy data:
                    var_out[:] = var_in[self.y[0] : self.y[1] - 1, self.x[0] : self.x[1]]
                else:
                    print("Variable dimensions could not be determined - skipping", var)
                    continue

            # Copy NetCDF attributes:
            for attr in var_in.ncattrs():
                # var_out.setncattr(attr, var_in.getncattr(attr))
                var_out.setncattr(attr, getattr(var_in, attr))

        if not grid_only:
            # data_vars = ['u','v','temp','salt']
            data_vars = ["u", "v"]

            if get3d:
                data_vars.extend(["zeta"])

            if include_wind:
                data_vars.extend([uwind, vwind])

            for var in data_vars:
                # Create variable in new file:
                var_in = nc_in.variables[var]
                coords = var_in.coordinates

                if get3d:
                    try:
                        dims = (
                            self.time_dimension[0],
                            var_in.dimensions[1],
                            var_in.dimensions[2],
                            var_in.dimensions[3],
                        )
                    except IndexError:  # no depth dimension (e.g. zeta)
                        dims = (
                            self.time_dimension[0],
                            var_in.dimensions[1],
                            var_in.dimensions[2],
                        )
                    if coords.find("lon_u") > -1:
                        var_out = nc_out.createVariable(var, var_in.dtype, dims)
                        # Copy data:
                        data = var_in[
                            t_index[0] : t_index[1] : t_index[2],
                            :,
                            self.y[0] : self.y[1],
                            self.x[0] : self.x[1] - 1,
                        ]
                    elif coords.find("lon_v") > -1:
                        var_out = nc_out.createVariable(var, var_in.dtype, dims)
                        # Copy data:
                        data = var_in[
                            t_index[0] : t_index[1] : t_index[2],
                            :,
                            self.y[0] : self.y[1] - 1,
                            self.x[0] : self.x[1],
                        ]
                    elif coords.find("lon_rho") > -1:
                        if len(var_in.dimensions) == 4:
                            var_out = nc_out.createVariable(var, var_in.dtype, dims)
                            # Copy data:
                            data = var_in[
                                t_index[0] : t_index[1] : t_index[2],
                                :,
                                self.y[0] : self.y[1],
                                self.x[0] : self.x[1],
                            ]
                        else:  # zeta does not have depth
                            var_out = nc_out.createVariable(var, var_in.dtype, dims)
                            # Copy data:
                            data = var_in[
                                t_index[0] : t_index[1] : t_index[2],
                                self.y[0] : self.y[1],
                                self.x[0] : self.x[1],
                            ]

                    else:
                        print(
                            "Variable dimensions could not be determined - skipping",
                            var,
                        )
                        continue
                else:  # surface only
                    try:
                        dims = (
                            self.time_dimension[0],
                            var_in.dimensions[2],
                            var_in.dimensions[3],
                        )
                    except IndexError:  # no depth dimension (e.g. wind)
                        dims = (
                            self.time_dimension[0],
                            var_in.dimensions[1],
                            var_in.dimensions[2],
                        )
                    if coords.find("lon_u") > -1:
                        var_out = nc_out.createVariable(var, var_in.dtype, dims)
                        # Copy data:
                        data = var_in[
                            t_index[0] : t_index[1] : t_index[2],
                            d_index,
                            self.y[0] : self.y[1],
                            self.x[0] : self.x[1] - 1,
                        ]
                    elif coords.find("lon_v") > -1:
                        var_out = nc_out.createVariable(var, var_in.dtype, dims)
                        # Copy data:
                        data = var_in[
                            t_index[0] : t_index[1] : t_index[2],
                            d_index,
                            self.y[0] : self.y[1] - 1,
                            self.x[0] : self.x[1],
                        ]
                    elif coords.find("lon_rho") > -1:
                        if len(var_in.dimensions) == 4:
                            var_out = nc_out.createVariable(var, var_in.dtype, dims)
                            # Copy data:
                            data = var_in[
                                t_index[0] : t_index[1] : t_index[2],
                                d_index,
                                self.y[0] : self.y[1],
                                self.x[0] : self.x[1],
                            ]
                        else:  # zeta does not have depth
                            var_out = nc_out.createVariable(var, var_in.dtype, dims)
                            # Copy data:
                            data = var_in[
                                t_index[0] : t_index[1] : t_index[2],
                                self.y[0] : self.y[1],
                                self.x[0] : self.x[1],
                            ]

                    else:
                        print(
                            "Variable dimensions could not be determined - skipping",
                            var,
                        )
                        continue

                # check for nans - replace with zero
                data = np.nan_to_num(data)
                var_out[:] = data

                # Copy NetCDF attributes:
                for attr in var_in.ncattrs():
                    if attr == "coordinates":
                        var_out.setncattr(attr, coords.replace("s_rho ", ""))
                    else:
                        if attr != "_FillValue":
                            # var_out.setncattr(attr, var_in.getncattr(attr))
                            var_out.setncattr(attr, getattr(var_in, attr))

        nc_out.close()
