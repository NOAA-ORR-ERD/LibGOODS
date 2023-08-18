from .metadata import Metadata
import model_catalogs as mc
from . import model_fetch, utilities, NonIntersectingSubsetError 

"""
This works specifically with model_catalogs using dask and xarray
Its leveraging a few methods in model_fetch.py that are specific to use with
xarray so I am not porting them to utilties until we decide which way to go with 
the code.
""" 
env_models = mc.setup()

def get_metadata():
    """
    """
    all_metas = {m: Metadata().init_from_model(env_models[m]) for m in env_models}
    return(all_metas)

def get_model_info(model_id,model_source,add_time_bounds=False):
    """
    Returns metadata about a particular model and (optionally) adds the 
    start end time of the selected source of the model output.
    This can be an expensive operation as it calls to_dask on the catalog
    """   
    try:
        cat = env_models[model_id]
    except KeyError:
        print(f"{model_id} is not a valid model name")       
    else:
        try:
            meta = Metadata().init_from_model(cat,source=model_source).as_pyson()        
            m = cat[model_source]
            meta['urlpath'] = m.urlpath #needed by nc4 code
            if add_time_bounds:
                mc.find_availability(m)            
                meta['actual_start'] = m.metadata['start_datetime']
                meta['actual_end'] = m.metadata['end_datetime']  
        except KeyError:
            print(f"{model_source} is not a valid source for this model")      
        else:
            return meta
     
def get_urllist_unagg(model_id,model_source,start,end,filename_only=False):

    '''
    Get a list of individual files needed to make an aggregation based on start/end dates
    
    :param model_id: A valid model ID for model_catalogs, e.g., 'CBOFS'
    :param model_source: Which source to request model files from, e.g. "coops-forecast-noagg'
    :param start: Requested model output start time (datetime)
    :param end: Requested model output end time (datetime)
    :param filename_only: Return only the file name - not the entire URL
    '''
    
    source = mc.select_date_range(env_models[model_id][model_source], start_date=start, end_date=end)
    
    fnames = source.urlpath
    
    if filename_only:
        fnames = [f.split('/')[-1] for f in fnames]
        
    
    return fnames


def generate_subset_xds(model_id,
                        model_source,
                        start,
                        end,
                        bounds,
                        surface_only,
                        cross_dateline,
                        var_list):

    '''
    Generates a subset xarray dataset. Does NOT actually get the data

    bounds: expects (w, s, e, n)
    '''

    cat = env_models[model_id]


    source = mc.select_date_range(cat[model_source], start_date=start, end_date=end)
    ds = source.to_dask()
    meta = get_model_info(model_id,model_source)


    ds = model_fetch.select_surface(ds)  # eventually check env params
    ds_ss = ds.em.filter(var_list)
    bounds = model_fetch.rotate_bbox(model_id, bounds)
    ds_ss = ds_ss.em.sub_grid(bbox=bounds)
    if meta["bounding_box"][2] > 180:
        ds_ss = model_fetch.rotate_longitude(ds_ss)

    return ds_ss

def request_subset(xds, output_pth):
    xds.to_netcdf(output_pth)
    return output_pth