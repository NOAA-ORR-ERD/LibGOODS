from .metadata import Metadata, ENVIRONMENTAL_PARAMETERS
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

def get_model_info(model_id,model_source):
    """
    Returns metadata about a particular model and adds the 
    start end time of the selected source of the model output.
    """   
    try:
        cat = env_models[model_id]
    except KeyError:
        print(f"{model_id} is not a valid model name")       
    else:
        meta = Metadata().init_from_model(cat).as_pyson()
        if model_source is not None:
            m = cat[model_source]
            mc.find_availability(m)            
            meta['actual_start'] = m.metadata['start_datetime']
            meta['actual_end'] = m.metadata['end_datetime']  
        return meta

        
def generate_subset_xds(identifier,
                        model_source,
                        start,
                        end,
                        bounds,
                        surface_only,
                        cross_dateline,
                        request_type):

    '''
    Generates a subset xarray dataset. Does NOT actually get the data

    bounds: expects (w, s, e, n)
    '''

    cat = env_models[identifier]

    polybounds = utilities.bbox2polygon(bounds)
    meta = Metadata().init_from_model(cat)
    if not utilities.check_subset_overlap(meta, [start, end], polybounds):
        # no overlap in at least one dimension
        raise NonIntersectingSubsetError()
    source = mc.select_date_range(cat[model_source], start_date=start, end_date=end)
    ds = source.to_dask()
    meta = get_model_info(identifier,model_source)
    if isinstance(request_type, list):
        env_params = [ENVIRONMENTAL_PARAMETERS[rt] for rt in request_type]
        env_params = [param for sublist in env_params for param in sublist] #flatten
    else:
        env_params = ENVIRONMENTAL_PARAMETERS[request_type]

    ds = model_fetch.select_surface(ds)  # eventually check env params
    ds_ss = ds.em.filter(env_params)
    bounds = model_fetch.rotate_bbox(meta["identifier"], bounds)
    ds_ss = ds_ss.em.sub_grid(bbox=bounds)
    if meta["bounding_box"][2] > 180:
        ds_ss = model_fetch.rotate_longitude(ds_ss)

    return ds_ss

def request_subset(xds, output_pth):
    xds.to_netcdf(output_pth)
    return output_pth