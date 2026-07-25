import warnings

import fsspec
import pandas as pd
import xarray as xr
import xarray_subset_grid

from libgoods.utilities import asdatetime, convert_longitude, flatten_bbox

from .base import BaseModel


class XSGBaseModel(BaseModel):
    '''
    Base class for all models that can be accessed/subset using xarray_subset_grid
    '''
    time_dims = None  # just so it's there
    def open_ds_tds(self, url):
        ds = xr.open_dataset(
            url,
            chunks=self.chunks,
            drop_variables=self.drop_variables,
        )
        return ds

    def open_ds_local(self, flist):
        ds = xr.open_mfdataset(
            flist,
            chunks=self.chunks,
            drop_variables=self.drop_variables,
            concat_dim=self.concat_dim,
            combine="nested",
            data_vars="minimal",
            coords="minimal",
            compat="override",
        )
        return ds

    def open_ds_zarr(self, s3_url):
        # open dataset as zarr object using fsspec reference file system and xarray
        fs = fsspec.filesystem(
            "reference",
            fo=s3_url,
            remote_protocol="s3",
            remote_options={"anon": True},
            target_protocol="s3",
            target_options={"anon": True},
        )
        m = fs.get_mapper("")

        ds = xr.open_dataset(
            m,
            engine="zarr",
            backend_kwargs=dict(consolidated=False),
            chunks=self.chunks,
            drop_variables=self.drop_variables,
        )
        return ds

    def open_ds(self):
        if self.access == "opendap":
            ds = self.open_ds_tds(self.location)
        elif self.access == "zarr":
            ds = self.open_ds_zarr(self.location)
        elif self.access == "local":
            ds = self.open_ds_local(self.location)
        else:
            print("Access method unknown")
            raise NotImplementedError

        self.ds = ds
        self.parse_time_dim_coords()
        t = self.ds[self.time_dims[0]] # this assumes variable and dimension have same name
        with warnings.catch_warnings():
            warnings.filterwarnings(
                action="ignore",
                message=".*Discarding nonzero nanoseconds.*",
                category=UserWarning)
            self.actual_start = pd.to_datetime(t.values[0]).to_pydatetime(t.values[0])
            self.actual_end = pd.to_datetime(t.values[-1]).to_pydatetime(t.values[-1])

    def size(self):
        return self.ds.nbytes

    def when(self):
        # we shouldn't have prints buried in here -- it should return the message
        # then you can print it -- or, in iPython, it will display it.
        try:
            return(f"{self.actual_start}\n{self.actual_end}")
        except AttributeError:
            return 'Dataset not opened -- call open_ds'

    def parse_time_dim_coords(self):
        '''
        Get time dimension coordinates (index coordinates).
        These are special, 1D coordinates that enable label-based indexing.
        Will be used in subset_time and to assign unlimited dimension when writing netcdf

        Note: This assumes that any coord with the word "time"
              in the name is a time coord.
              It also checks for standard_name: 'time', though
              that's not well tested.

        (see GFS dataset which has most complexity)
        '''

        # old code -- a bit klunkier
        # # coords = list(self.ds.coords)
        # coords = self.ds.coords
        # dims = list(self.ds.dims)
        # # tdim = [d for d in dims if d.find('time')>=0 and d in coords]
        # tdim = [d for d in dims if 'time' in d and d in self.ds.coords]

        tdim = [d for d in self.ds.xindexes
                if ('time' in d)
                or (self.ds[d].attrs.get('standard_name') == 'time')]

        self.time_dims = tdim

    def subset_time(self, start_time, end_time):
        """
        Subset the model results in time.

        model results are restricted to the specified time bounds.

        model changed in-place

        Parameters
        ----------
        start_time : str or datetime
            The start time for the subset window.
        end_time : str or datetime
            The end time for the subset window.

        """
        # Should include the time series inclusive of start and end dates
        #
        # self.time_dims is a list as some datasets have more than one time variable

        start_time = asdatetime(start_time)
        end_time = asdatetime(end_time)

        if self.time_dims is None:
            self.parse_time_dim_coords()

        # loops through all the time dimensions
        # and subsets them all, one by one.
        for tdim in self.time_dims:
            if start_time is not None:
                try:
                    best_start = self.ds[tdim].sel({tdim: start_time}, method='ffill')
                except KeyError as err:
                    msg = (f"invalid start_time: {start_time}. Available range is: "
                          f"{self.actual_start} {self.actual_end}")
                    raise ValueError(msg) from err
            else:
                best_start = None

            if end_time is not None:
                try:
                    best_end = self.ds[tdim].sel({tdim: end_time}, method='bfill')
                except KeyError as err:
                    msg = (f"invalid end_time: {end_time}. Available range is: "
                          f"{self.actual_start} {self.actual_end}")
                    raise ValueError(msg) from err

            else:
                best_end = None

            self.ds = self.ds.sel({tdim: slice(best_start, best_end)})


    def subset_grid(self, bbox):
        # TODO: Add check on bbox and ds longitude to see if they are
        #       using same convention (0-->360 vs -180-180)
        #  NOTE: XSG does something with this -- not sure what though ...
        bbox = flatten_bbox(bbox)
        self.ds = self.ds.xsg.subset_bbox(bbox)

    def select_surface(self, level_depth=0):
        """
        Pull out only the surface layer
        """
        # subset_vertical_level uses sel based on vertical coord = 0 (e.g, z=0)
        self.ds = self.ds.xsg.subset_vertical_level(level=level_depth, method='nearest')

    def filter_variables(self, variable_list=None, get3d=False):
        # This one is for surface only models (used by HFradar)
        # variable list default is based on surface u/v variable names
        if variable_list is None:
            variable_list = ["eastward_sea_water_velocity", "northward_sea_water_velocity"]

        vars2include = [self.standard_names[v] for v in variable_list]

        self.ds = self.ds.xsg.subset_vars(vars2include)
        self.parse_time_dim_coords()

    def normalize_longitude(self):
        """
        normalizes the longitude for output

        """
        lon_coords = self.ds.cf.coordinates.get("longitude")

        for lc in lon_coords:
            lon_var = self.ds[lc]
            shifted = convert_longitude(lon_var.data, coord_system='-180--180')
            new_lon = lon_var.copy(data=shifted)
            new_lon.attrs.pop('modulo', None) # from EPSG model (It's set to '360 degrees')
            self.ds = self.ds.assign_coords(**{lc: new_lon})

    def write_nc(self, ofn="test.nc", close_ds=True):
        """
        write the netCDF file
        """
        # NOTE: we used to get an error on something with the unlimited_dims flag
        #       it may crop up again, and could be wrapped in a try: except.
        try:
            self.ds.to_netcdf(ofn, unlimited_dims=self.time_dims)
        except ValueError: # GFS has something weird with unlimited dims that xarray barfs on
            self.ds.to_netcdf(ofn)
        if close_ds:
            self.ds.close()

class FVCOM(XSGBaseModel):
    chunks = {"siglay": 1, "siglev": 1, "time": 1}
    drop_variables = ["Itime", "Itime2"]
    standard_names = {
        "eastward_sea_water_velocity": "u",
        "eastward_wind": "uwind_speed",
        "northward_sea_water_velocity": "v",
        "northward_wind": "vwind_speed",
        "upward_sea_water_velocity": "ww",
        "sea_floor_depth": "h",
        "sea_surface_elevation": "zeta",
        "sea_water_temperature": "temp",
        "sea_water_practical_salinity": "salinity",
    }
    zcoord = ["sigma_layers", "sigma_levels"]
    access = None
    location = None

    def open_ds(self):
        super().open_ds()
        self.ds = xarray_subset_grid.grids.ugrid.assign_ugrid_topology(
            self.ds, face_node_connectivity="nv"
        )

    def filter_variables(self, variable_list=None, get3d=False):
        # variable list default is based on surface u/v variable names
        if variable_list is None:
            variable_list = [
                    "eastward_sea_water_velocity",
                    "northward_sea_water_velocity"]

        if get3d:
            variable_list.extend(["upward_sea_water_velocity",
                                  "sea_surface_elevation",
                                  "sea_floor_depth"])

        vars2include = [self.standard_names[v] for v in variable_list]

        # xarray subset grid should be smart enough to include these but its not
        if get3d:
            vars2include.extend(["siglay"])

        self.ds = self.ds.xsg.subset_vars(vars2include)

    def select_surface(self, siglay=0):
        # siglay = 0 for surface, siglay=1 for bottom
        # xsg uses sel but the siglay is 2d (depth,nodes) so incompatible *sometimes*
        self.ds = self.ds.isel(siglay=siglay)


class ROMS(XSGBaseModel):
    chunks = {"s_rho": 1, "s_w": 1, "time": 1}
    drop_variables = None
    standard_names = {
        "eastward_sea_water_velocity": "u",
        "eastward_wind": "Uwind",
        "northward_sea_water_velocity": "v",
        "northward_wind": "Vwind",
        "upward_sea_water_velocity": "w",
        "sea_floor_depth": "h",
        "sea_surface_elevation": "zeta",
        "sea_water_temperature": "temp",
        "sea_water_practical_salinity": "salt",
    }
    zcoord = "sigma_layers"
    access = None
    location = None

    def filter_variables(self, variable_list=None, get3d=False):
        # variable list default is based on surface u/v variable names
        if variable_list is None:
            variable_list = [
                    "eastward_sea_water_velocity",
                    "northward_sea_water_velocity",
                ]

        if get3d:
            variable_list.extend(["sea_surface_elevation",
                                  "sea_floor_depth"])

        # xarray subset grid should be smart enough to include these but its not
        vars2include = [self.standard_names[v] for v in variable_list]
        vars2include.extend(["angle", "mask_rho", "mask_psi", "mask_u", "mask_v"])
        if get3d:
            vars2include.extend(["Cs_r", "Cs_w", "hc", "Vtransform"])

        self.ds = self.ds.xsg.subset_vars(vars2include)
