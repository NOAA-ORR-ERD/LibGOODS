from . import file_processing, utilities
from .metadata import Metadata, ENVIRONMENTAL_PARAMETERS
from netCDF4 import Dataset, num2date
"""
This leverages Amy's old libGOODS code to determine subset size and write the output
"""

def add_time_bounds(meta,tvar):
    """
    Adds the start/end times to the metadata object
    """   
          
    model = file_processing.base.nc()
    model.open_nc(FileName=meta['urlpath'], tvar=tvar)
    meta['actual_start'] = model.start_date
    meta['actual_end'] = model.end_date
    return meta
        
def get_model_subset(    
    url,
    start,
    end,
    bounds,
    surface_only=True,
    cross_dateline=False,
    var_list=[],
    grid=None
    ):

    """

    :param model_id: ID (name) of the model
    :param model_source (forecast/nowcast etc) -- !!!naming conventions are changing soon
    :params start: start time of to subset to (date string)
    :params end: end time to subset to (date string)
    :param bounds: bounds to subset to -- (using [x1,y1,x2,y2] format at present
    :param surface_only: limit to surface values in model output
    :param cross_dateline=False: whether the subset crosses the dateline
    :param environmental_parameters: which environmental parameters to extract

    :returns: file processing model object
    """
    #source = mc.select_date_range(cat[model_source], start_date=start, end_date=end)
    if 'eastward_wind' in var_list:
        include_wind = True
    else:
        include_wind = False

    
    if grid == "ROMS":
        model = file_processing.roms()
        if isinstance(url,list):
            var_map = {"time": "ocean_time"}
        else:
            var_map = {"time": "time"}
    elif grid == "POM":
        var_map = {"time": "time", "lon": "lon", "lat": "lat", "u": "u", "v": "v"}
        model = file_processing.curv()
    else:
        var_map = {
            "time": "time",
            "lon": "lon",
            "lat": "lat",
            "u": "water_u",
            "v": "water_v",
        }
        model = file_processing.rect()

    model.open_nc(url)
    # get dimensions to determine subset
        
    model.get_dimensions(var_map=var_map)
    if model.lon.max() > 180:  # should model catalogs tell us the coordinates?
        bounds[0] = bounds[0] + 360
        bounds[2] = bounds[2] + 360

    t1, t2 = model.get_timeslice_indices(start, end)
    # grid subsetting
    model.subset(bounds)
    #model.write_nc(var_map=var_map, ofn=target_pth, t_index=[t1, t2, 1])
    
    #strip Dataset so it can be pickled and add source urlpath and other params
    model.Dataset = None;
    model.GridDataset = None;
    model.urlpath = url
    model.tindex = [t1,t2, 1]
    model.nbytes = 1000 #api will look for this -- have to figure out how to add something
    model.is3d = not(surface_only)
    model.var_map = var_map
    model.include_wind = include_wind
    
    return model

    
def get_model_output(model, output_pth):

    model.update(model.urlpath) #this was removed for api (nc4 Dataset can't be pickled)
    model.write_nc(var_map=model.var_map,ofn=output_pth,t_index=model.tindex,is3d=model.is3d,include_wind=model.include_wind)
    
    