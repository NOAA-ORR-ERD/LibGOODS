import xarray as xr
import extract_model as em
import os

def get_model_subset(    
    fpath,
    start, #ignored at this point - need to implement
    end, #ignored at this point
    bounds,
    var_list,
    surface_only=True,
    cross_dateline=False,
    model_type=None,
    drop_variables=None,
    out_dir=None,
    ):
    
    if not list(fpath):
        fpath = [fpath,]
    
    if model_type in ['FVCOM','SELFE','ADCIRC']:
        engine= 'triangularmesh_netcdf'
    else:
        engine = None
    
    if out_dir is None:
        out_dir = '.'
    
    newfilelist = []
    for f in fpath:
        
        fname=os.path.split(f)[-1].split('.nc')[0] + '_ss.nc'
        
        ofname = os.path.join(out_dir, fname)
        
        ds = xr.open_dataset(f, engine=engine, decode_times=True, drop_variables=drop_variables, chunks={'time':1})
        
        ds = em.preprocess(ds)
        ds_ss = ds.em.filter(var_list, model_type=model_type)
        ds_ss = ds.em.sub_grid(bbox=bounds, model_type=model_type)
       
        
        ds_ss.to_netcdf(ofname,unlimited_dims='time')
        
        newfilelist.append(ofname)
        ds.close()
        ds_ss.close()
        
        
    return newfilelist
    
    
    
