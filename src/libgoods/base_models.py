import tempfile
import fsspec
import xarray as xr
import xarray_subset_grid

class base:

    def open_ds_tds(self,url):
        ds = xr.open_dataset(url,
                             chunks=self.chunks,
                             drop_variables=self.drop_variables,
                             )
        return ds

    def open_ds_local(self,flist):
        ds = xr.open_dataset(flist,
                               chunks=self.chunks,
                               drop_variables=self.drop_variables,
                               )
        return ds

    def open_ds_zarr(self,s3_url):
        #sample url: "s3://nextgen-dmac-cloud-ingest/nos/ngofs2/nos.ngofs2.2ds.best.nc.zarr"
        # open dataset as zarr object using fsspec reference file system and xarray
        fs = fsspec.filesystem("reference",fo=s3_url,
                               remote_protocol="s3",
                               remote_options={"anon": True},
                               target_protocol="s3",
                               target_options={"anon": True},
                               )
        m = fs.get_mapper("")

        ds = xr.open_dataset(m,
                             engine="zarr",
                             backend_kwargs=dict(consolidated=False),
                             chunks=self.chunks,
                             drop_variables=self.drop_variables,
                             )
        return ds

    def check_ds_size(self):
        print('Aggregation size is:')
        print(f'{self.ds.nbytes / 1e9:.5} GB')

    def check_agg_time(self):
        t = self.ds[self.tvar]
        print('Aggregation start/end times:')
        print(t.values[0])
        print(t.values[-1])

    def subset_time(self,start_time,end_time):
         #TODO: make this smarter to use > start and/or < end etc (one end is None)
        self.ds = self.ds.sel({self.tvar:slice(start_time,end_time)})


    def subset_grid(self,bbox):

        if self.grid_type == 'unstructured' and self.access == 'opendap':
            #download first
            tf = tempfile.NamedTemporaryFile(delete=False) #not sure how to clean this up
            self.ds.to_netcdf(tf.name)
            self.ds = xr.open_dataset(tf.name)
            tf.close()
        else:
            self.ds = self.ds.xsg.subset_bbox(bbox)


    def write_nc(self,ofn='test.nc',close_ds=True):

        self.ds.to_netcdf(ofn,unlimited_dims=self.tvar)
        if close_ds:
            self.ds.close()

class fvcom(base):

    def __init__(self,
                 chunks = {'time':1},
                 drop_variables = ["Itime2"],
                 standard_names = {
                    'eastward_sea_water_velocity': 'u',
                    'eastward_wind': 'uwind_speed',
                    'northward_sea_water_velocity': 'v',
                    'northward_wind': 'vwind_speed',
                    'upward_sea_water_velocity': 'ww',
                    'sea_floor_depth': 'h',
                    'sea_surface_elevation': 'zeta',
                    'sea_water_temperature': 'temp',
                    'sea_water_practical_salinity': 'salinity',
                    },
                 tvar = 'time',
                 zcoord = ['sigma_layers','sigma_levels'],       access = None,
                 location = None                 
                 ):

         self.grid_type = 'unstructured'
         self.chunks = chunks
         self.drop_variables = drop_variables
         self.standard_names = standard_names
         self.tvar = tvar
         self.zcoord = zcoord
         self.access = access
         self.location = location

    def open_ds(self):
        if self.access == 'opendap':
            ds = self.open_ds_tds(self.location)
        elif self.access == 'zarr':
            ds = self.open_ds_zarr(self.location)
        elif self.access == 'local':
            ds = self.open_ds_local(self.location)
        else:
            print('Access method unkwown')
            raise NotImplementedError

        self.ds = xarray_subset_grid.grids.ugrid.assign_ugrid_topology(ds,face_node_connectivity="nv")

    def filter_variables(self,variable_list=None,is3d=False):

        if variable_list is None:
            variable_list = ['eastward_sea_water_velocity','northward_sea_water_velocity']
            if is3d:
                variable_list.extend(['sea_surface_elevation','sea_floor_depth','upward_sea_water_velocity'])

        vars2include = [self.standard_names[v] for v in variable_list]

        if is3d:
            vars2include.extend(['siglay','siglev'])

        self.ds = self.ds.xsg.subset_vars(vars2include)

    def select_surface(self):

        self.ds = self.ds.isel(siglay=0)


class roms(base):

    def __init__(self,
                 chunks = None,
                 drop_variables = None,
                 standard_names = {
                    'eastward_sea_water_velocity': 'u',
                    'surface_eastward_sea_water_velocity': 'u_sur',
                    'eastward_wind': 'uwind_speed',
                    'northward_sea_water_velocity': 'v',
                    'surface_northward_sea_water_velocity': 'v_sur',
                    'northward_wind': 'vwind_speed',
                    'upward_sea_water_velocity': 'w',
                    'angle': 'angle',
                    'sea_floor_depth': 'h',
                    'sea_surface_elevation': 'zeta',
                    'sea_water_temperature': 'temp',
                    'sea_water_practical_salinity': 'salinity',
                    },
                 tvar = 'ocean_time',
                 zcoord = 'sigma_layers',
                 access = None,
                 location = None                    
                 ):

         self.grid_type = 'curvilinear',
         self.chunks = chunks
         self.drop_variables = drop_variables
         self.standard_names = standard_names
         self.tvar = tvar
         self.zcoord = zcoord
         self.access = access
         self.location = None

    def open_ds(self):

        if self.access == 'opendap':
            ds = self.open_ds_tds(self.location)
        elif self.access == 'zarr':
            ds = self.open_ds_zarr(self.location)
        elif access == 'local':
            self.ds = self.open_ds_local(self.location)
        else:
            print('Access method unknown')
            raise NotImplementedError

        self.ds = ds

    def filter_variables(self,variable_list=None,is3d=False):
        #variable list default is based on surface u/v variable names
        if variable_list is None:
            variable_list = ['surface_eastward_sea_water_velocity','surface_northward_sea_water_velocity']
            #need to always add all grid vars including masks -- then add optional vars from there.

        vars2include = [self.standard_names[v] for v in variable_list]
        vars2include.extend(['angle','mask_rho','mask_psi','mask_u','mask_v'])
        if is3d:
            vars2include.extend(['Cs_r','Cs_w','hc','Vtransform'])#add zeta, h etc.
        self.ds = self.ds.xsg.subset_vars(vars2include)

    def select_surface(self):

        #self.ds = self.ds.xsg.subset_vertical_level(level=0, method='nearest')
        self.ds = self.ds.isel(s_rho=-1)
            # self.ds = self.ds.drop_vars('siglay')
            # self.ds = self.ds.drop_vars('siglev')
