"""
Core API for accessing model results

These are the functions that the WebGNOME client will call


"""


import os
import numpy as np

from . import FileTooBigError, NonIntersectingSubsetError, file_processing, utilities, model_catalogs

def list_models(model_ids_sources=None, map_bounds=None, env_params=None, as_pyson=False):
    """
    Return metadata for all available models

    This is the static information about the models

    :param model_ids=None: Optional dict of particular models names (keys) and sources (list). If None
                           all available models will be returned
    :param model_sources=None: Optional dict of which source(s) to include for each model. If None
                           all available sources will be returned
    :param map_bounds: Bounds within which the models can overlap, if None, the whole world

    :param env_params=None: Only provide models that have the given parameters

    :param as_pyson=False: If True, result is JSON-compatible dict.
                           If false, Metadata objects.

    :returns: list of metadata for models that satisfy the criteria

    """
    all_metas = model_catalogs.get_metadata();
    retval = utilities.filter_models(
        all_metas.values(),
        model_ids_sources=model_ids_sources,
        map_bounds=map_bounds,
        env_params=env_params,
    )
       
    if as_pyson:
        retval = [m.as_pyson() for m in retval]
    return retval


def get_model_info(model_id,model_source=None):
    """
    Return metadata about a particular model

    :param model_id: the name (unique ID) of the model
    :param model_source: the source the model output is being requested from. Will also add 
    actual_start/end to the metadata

    :returns: libgoods.metadata.Metadata object with metadata of the model.

    TODO?? -- return only meta for specific source?

    """
    meta = model_catalogs.get_model_info(model_id,model_source)
    return meta

def get_model_ss(   
    model_id,
    model_source,
    start,
    end,
    bounds,
    surface_only=True,   
    cross_dateline=False,
    environmental_parameters="surface currents"):
    """
   
    
    """
    ds = model_catalogs.generate_subset_xds(model_id,
                                            model_source,
                                            start,
                                            end,
                                            bounds,
                                            surface_only,
                                            cross_dateline,
                                            environmental_parameters)
                                       
    return ds

    

def get_model_output(xds, output_pth):

    output_path = model_catalogs.request_subset(xds, output_pth)

    return output_pth
    
    
def get_model_file(   
    model_id,
    model_source,
    start,
    end,
    bounds,
    surface_only=True,
    environmental_parameters="surface currents",
    # cross_dateline=False,
    # max_filesize=None,
    target_pth=None,
    method=0, #0=new code, 1=Amy's old code
):
    """
    Get the actual model data as a netcdf file. NOT USED BY WebGNOME!!
    left here for now but probably don't need this anymore.

    :param model_id: ID (name) of the model
    :param model_source (forecast/nowcast etc) -- !!!naming conventions are changing soon
    :params start: start time of to subset to (date string)
    :params end: end time to subset to (date string)
    :param bounds: bounds to subset to -- (using (x1,y1,x2,y2) format at present


    :param environmental_parameters: which environmental parameters to extract

    :param cross_dateline=False: whether the subset crosses the dateline

    :param max_filesize = None: maximum filesize to generate -- if the file will
                          be larger than this, raise a FileTooBigError

    :param target_dir: full path of file to write the output too -- if None, it will be put in a temp dir or local dir.


    :returns: filepath
    """

    if target_pth is None:
        target_pth = os.path.abspath("output.nc")

    cat = env_models[model_id]

    polybounds = utilities.bbox2polygon(bounds)
    if not check_subset_overlap(cat, [start, end], polybounds):
        # no overlap in at least one dimension
        raise NonIntersectingSubsetError()


    meta = get_model_info(model_id)
   
    source = mc.select_date_range(cat[model_source], start_date=start, end_date=end)
    
    if method==0:       
        ds = source.to_dask()
        target_pth = model.fetch_model(ds, meta, bounds, target_pth, which_data=environmental_parameters)
    else:
        model.fetch_model_oldcode(source.urlpath,meta,bounds,start,end,target_pth)
    
    return target_pth
