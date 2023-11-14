import xarray as xr
import extract_model as em
import os

def select_surface(ds): 
    #from Luke's code in "model_fetch" -- needs to be improved
    """Return a dataset that is reduced to only the surface layer."""
    model_guess = em.utils.guess_model_type(ds)
    # SELFE uses a hybrid sigma coordinate system for the vertical coordinates,
    # but cf_xarray misinterprets it as being the z variable. So, we check SELFE
    # first, before trying to use cf_xarray
    if model_guess == "SELFE":
        return ds.isel(nv=-1)
    elif model_guess == "FVCOM":
        # vertical_dims = set()
        # for varname in ds.cf.axes["Z"]:
            # vertical_dim = ds[varname].dims[0]
            # vertical_dims.add(vertical_dim)
        # sel_kwargs = {vdim: 0 for vdim in vertical_dims}
        # return ds.isel(**sel_kwargs)
        return ds.isel(siglay=-1) #not sure if this is right
    elif all([ds[zaxis].ndim < 2 for zaxis in ds.cf.axes["Z"]]):
        return ds.cf.sel(Z=0, method="nearest")
    raise ValueError("Can't decode vertical coordinates.")

def rotate_bbox(bbox):
    """
    If the bounding box uses [-180, 180] and the model uses [0, 360] the
    bounding box elements are shifted into the domain.
    """
    new_bbox = list(bbox)
    if new_bbox[0] < 0:
        new_bbox[0] += 360
    if new_bbox[2] < 0:
        new_bbox[2] += 360
    return tuple(new_bbox)

    
def get_model_subset(    
    fpath,
    start=None, 
    end=None, 
    bounds=None,
    snames_of_vars_to_include=None,
    var_list=None,
    surface_only=True,
    model_type=None,
    out_dir=None,
    ):
    
    if not type(fpath) is list:
        fpath = [fpath,]
        
    if model_type in ['FVCOM','SELFE','ADCIRC']:
        engine = 'triangularmesh_netcdf'
    else:
        engine = None
    
    preload_varmap = None
    drop_variables = None
    if model_type == 'FVCOM':
        drop_variables = ['Itime', 'Itime2']
        #preload_varmap = {'siglay': 'sigma_layers','siglev': 'sigma_levels'}
        preload_varmap = {'siglay': 'sigma_layers'} #NECOFS
        bounds = rotate_bbox(bounds) #TODO: need to determine if necessary
        
    if out_dir is None:
        out_dir = '.'
    
    newfilelist = []
    time_dim = None #not sure why I did this? should it be a passed in option?
    get_time_units = True
    
    for f in fpath:
        #this derives the saved file name from the input -- should probably have option to pass in desired name

        if os.path.exists(f): #local file
            fname=os.path.split(f)[-1].split('.nc')[0] + '_ss.nc' 
        else: #url
            fname=f.split('/')[-1]
        ofname = os.path.join(out_dir, fname)

        if os.path.exists(ofname):
            print('Already subset ', fname)
        
        else:
            print(f)
            if preload_varmap is None: #this keyword only works with triangularmesh "engine". Ugh.
                ds = xr.open_dataset(f, engine=engine, decode_times=True, drop_variables=drop_variables)
            else:
                ds = xr.open_dataset(f, engine=engine, decode_times=True, preload_varmap=preload_varmap, drop_variables=drop_variables)

            #ds = em.preprocess(ds) #this can take a really long time

            #get time units from first file then use this when writing subsequent files so they all have the same time base
            if get_time_units:
                t_units = ds.time.encoding['units']
                get_time_units = False

            if start is not None and end is not None:
                #TODO: make this smarter to use > start and/or < end etc
                ds = ds.sel(time=slice(start,end))

            if snames_of_vars_to_include:
                ds = ds.em.filter(snames_of_vars_to_include, model_type=model_type,keep_vertical_coords=keep_vertical_coords) 
                
            #do this before surface indexing or else it tanks
            if bounds is not None:
                ds = ds.em.sub_grid(bbox=bounds, model_type=model_type) 
                
            if surface_only:
                ds = select_surface(ds)
                keep_vertical_coords = False
            else:
                keep_vertical_coords = True

            if time_dim is None:
                for td in ['time','ocean_time','MT','T']:
                    try:
                        ds.dims[td]
                        time_dim = td
                        break
                    except KeyError: #then what?
                        pass

            ds.time.encoding['units'] = t_units

            ds.to_netcdf(ofname,unlimited_dims=time_dim)
            ds.close()  
    
        newfilelist.append(ofname)
                
    return newfilelist
    
    
def concat(newfiles,ofn):

    ds = xr.open_mfdataset(newfiles)
    ds.to_netcdf(ofn)
    
