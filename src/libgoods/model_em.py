import xarray as xr
import extract_model as em
import os
from pathlib import Path

# def select_surface(ds): 
    # #from Luke's code in "model_fetch" -- needs to be improved
    # """Return a dataset that is reduced to only the surface layer."""
    # model_guess = em.utils.guess_model_type(ds)
    # print(model_guess)
    # # SELFE uses a hybrid sigma coordinate system for the vertical coordinates,
    # # but cf_xarray misinterprets it as being the z variable. So, we check SELFE
    # # first, before trying to use cf_xarray
    # if model_guess == "SELFE":
        # return ds.isel(nv=-1)
    # elif model_guess == "FVCOM":
        # # vertical_dims = set()
        # # for varname in ds.cf.axes["Z"]:
            # # vertical_dim = ds[varname].dims[0]
            # # vertical_dims.add(vertical_dim)
        # # sel_kwargs = {vdim: 0 for vdim in vertical_dims}
        # # return ds.isel(**sel_kwargs)
        # return ds.isel(siglay=0) #not sure if this is right
    # elif all([ds[zaxis].ndim < 2 for zaxis in ds.cf.axes["Z"]]):
        # return ds.cf.sel(Z=0, method="nearest")
    # raise ValueError("Can't decode vertical coordinates.")

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
    new_fname=None, #this won't work with a list of files
    start=None, 
    end=None, 
    bounds=None,
    snames_of_vars_to_include=None,
    tvar_name='time',
    tcoord_name='time',
    drop_variables=None,
    chunks=None,
    out_dir=None,
    fname=None,
    check_exists=True,
    surface_index=None,
    ):
    """
    WARNING: This is in progress and many parts are hard coded in for special cases and may not be what you want. Needs attention once I figure out how to do things generically in xarray
    """
        
    if not type(fpath) is list:
        fpath = [fpath,]
               
    if out_dir is None:
        out_dir = '.'
    
    newfilelist = []   
    file0=1
    
    for f in fpath:
        
        if new_fname is None: #make filename from url or local file
            if Path(f).exists(): #local file
                fname = '_ss.'.join(Path(f).name.split('.')) #this is ugly if there is more than one "." in the filename
            elif f.find('http')==0: #url
                fname = f.split('/')[-1]
            ofname = Path(out_dir) / fname
        else:        
            ofname = Path(out_dir) / new_fname

        if check_exists and Path(ofname).exists():
            print('Already subset ', f)
        
        else:
        
            if drop_variables:
                if all(x in drop_variables for x in ['Itime', 'Itime2']):
                #TODO add some special FVCOM crap to deal with this
                    pass
        
            ds = xr.open_dataset(f, decode_times=True, drop_variables=drop_variables,chunks=chunks)
   
            if file0: ###this only works with specific var names
                t_units = ds.variables[tvar_name].encoding['units']
                file0 = False
                #need generic lon check
                #lon_snames = ds.cf.standard_names['grid_longitude_at_cell_center']
                # lon = ds['lon'].values #AARgH
                # if lon.max() >= 180:
                    # bounds = rotate_bbox(bounds)
                #ADD check for lon bounds

            if start is not None and end is not None:
                #TODO: make this smarter to use > start and/or < end etc (one end is None)
                ds = ds.sel({tcoord_name:slice(start,end)})
                            
            #do this before surface indexing or else it tanks
            if bounds is not None:
                ds = ds.em.sub_grid(bbox=bounds) 
            
            keep_vertical_coords = True            
            if surface_index is not None:
                #ds = select_surface(ds)
                ds = ds.cf.sel(Z=0, method="nearest")
                
                # ds = ds.isel(siglay=0)
                # ds = ds.isel(siglev=0)
                keep_vertical_coords = False
                
            if snames_of_vars_to_include:
                ds = ds.em.filter(snames_of_vars_to_include,keep_vertical_coords=keep_vertical_coords) 

            #keep original units and reference all to first file
            #ds.time.encoding['units'] = t_units
            
            # ds.variables['lonc'].data = ds.variables['lonc'].data - 360
            # ds.variables['lon'].data = ds.variables['lon'].data - 360
            
            ds.to_netcdf(ofname,unlimited_dims=tcoord_name)
            ds.close()  
    
        newfilelist.append(ofname)
                
    return newfilelist
    
    
def concat(newfiles,ofn):

    ds = xr.open_mfdataset(newfiles)
    ds.to_netcdf(ofn)
    
