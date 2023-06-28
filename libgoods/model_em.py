import xarray as xr
import extract_model as em
import os

def select_surface(ds):
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
        return ds.isel(siglay=-1)
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
    start, #ignored at this point - need to implement
    end, #ignored at this point
    bounds,
    var_list=None,
    surface_only=True,
    model_type=None,
    out_dir=None,
    ):
    
    if not list(fpath):
        fpath = [fpath,]
    
        
    if model_type in ['FVCOM','SELFE','ADCIRC']:
        engine= 'triangularmesh_netcdf'
    else:
        engine = None
    
    preload_varmap = None
    drop_variables = None
    if model_type == 'FVCOM':
        drop_variables = ['Itime', 'Itime2']
        preload_varmap = {'siglay': 'sigma_layers', 'siglev': 'sigma_levels'}
        bounds = rotate_bbox(bounds)
        
    if out_dir is None:
        out_dir = '.'
    
    newfilelist = []
    time_dim = None
    for f in fpath:
       
        fname=os.path.split(f)[-1].split('.nc')[0] + '_ss.nc'
        
        ofname = os.path.join(out_dir, fname)
        
        ds = xr.open_dataset(f, engine=engine, decode_times=False, preload_varmap = preload_varmap, drop_variables=drop_variables)
        

                
        ds = em.preprocess(ds)
        
        if surface_only:
            ds = select_surface(ds)
            keep_vertical_coords = False
        else:
            keep_vertical_coords = True
        #ds_ss = ds.em.filter(var_list, model_type=model_type,keep_vertical_coords=keep_vertical_coords) #filtering on variables and not keeping vertical coords is not working in extract_model or i am doing something wrong

        ds_ss = ds.em.sub_grid(bbox=bounds, model_type=model_type)      
        
        if time_dim is None:
            for td in ['time','ocean_time','MT','T']:
                try:
                    ds.dims[td]
                    time_dim = td
                    break
                except KeyError:
                    pass
        ds_ss.to_netcdf(ofname,unlimited_dims=time_dim)
        
        newfilelist.append(ofname)
        ds.close()
        ds_ss.close()
        
        
    return newfilelist
    
    
    
