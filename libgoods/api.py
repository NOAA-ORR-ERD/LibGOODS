"""
Core API for accessing model results

These are the functions that the WebGNOME client will call


"""
import os
import numpy as np

from . import utilities, model_dask, model_nc4, NonIntersectingSubsetError 
from .metadata import get_var_list_standard_names, filter_var_map


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
    all_metas = model_dask.get_metadata()
    retval = utilities.filter_models(
        all_metas.values(),
        model_ids_sources=model_ids_sources,
        map_bounds=map_bounds,
        env_params=env_params,
    )
       
    if as_pyson:
        retval = [m.as_pyson() for m in retval]
    return retval


def get_model_info(model_id,model_source,axiom=False):
    """
    Return metadata about a particular model from a particular access source

    :param model_id: the name (unique ID) of the model
    :param model_source: the source the model output is being requested from. Will also add 
    actual_start/end to the metadata

    :returns: libgoods.metadata.Metadata object with metadata of the model and source.

    TODO?? -- return only meta for specific source?

    The axiom pathway uses model_catalogs.find_availability which can be slow
    Otherwise, we use a netCDF4 variable retrieval to get the start/end date based on the url
    """
    if axiom or ('noagg' in model_source):
        meta = model_dask.get_model_info(model_id,model_source,add_time_bounds=True)
    else:
        meta = model_dask.get_model_info(model_id,model_source) #use the model_catalogs code to        
        tvar_name = meta['sources'][0]['standard_names']['time']
        meta = model_nc4.add_time_bounds(meta,tvar_name)
    return meta

def get_model_subset(   
    model_id,
    model_source,
    start,
    end,
    bounds,
    surface_only=True,   
    cross_dateline=False,
    environmental_parameters="surface currents",
    axiom=False):
    """
    The nc4 code returns a model object that has info about the grid and subset indices
    The dask code returns an xarray dataset -- both work ok with api (can be pickled)
    
    """
    polybounds = utilities.bbox2polygon(bounds)
    meta = get_model_info(model_id,model_source)
    
    if not utilities.subset_intersects_model_boundary(meta['bounding_poly'], polybounds):
        # no overlap in at least one dimension
        raise NonIntersectingSubsetError()
        
    var_list = get_var_list_standard_names(environmental_parameters)
            
    if axiom:
        ds = model_dask.generate_subset_xds(model_id,
                                            model_source,
                                            start,
                                            end,
                                            bounds,
                                            surface_only,
                                            cross_dateline,
                                            var_list)
    else:
        
        #build url list if unaggregated
        if 'noagg' in model_source: 
            urlpath = model_dask.get_urllist_unagg(model_id,model_source,start,end)
        else:
            urlpath = meta['urlpath']
        
        var_map = filter_var_map(var_list, meta['sources'][0]['standard_names'])
        try:            
            ds = model_nc4.get_model_subset(urlpath,
                                    start,
                                    end,
                                    list(bounds),
                                    surface_only=surface_only,
                                    cross_dateline=cross_dateline,
                                    var_map = var_map,
                                    grid = meta['grid_type'])
        except:
            ds = None
                                            
                              
    return ds

    

def get_model_output(xds, output_pth, axiom=False):

    if axiom:
        output_path = model_dask.request_subset(xds, output_pth)
    else:
        try:
            output_path = model_nc4.get_model_output(xds, output_pth)
        except:
            output_path = None
    
    return output_pth
    
    

