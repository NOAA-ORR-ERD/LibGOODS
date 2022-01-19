import os
import json
from libgoods import rect_model, roms_model, temp_files_dir, currents_dir

def list_models():
    '''
    list all available models
    '''
    pass
    
def get_all_boundaries():
    '''
    get boundaries from all models
    '''
    pass

def get_currents(model_name,
            north_lat,
            south_lat,
            west_lon,
            east_lon,
            cross_dateline=False,
            max_filesize=None,
            ):
            
    model_file = os.path.join(currents_dir, model_name + '.json')
    
    with open(model_file, 'r') as f:
        model_info = json.load(f)
         
    url = model_info['url']
    var_map = model_info['var_map']
    grid_type = model_info['grid_type']
    
    if grid_type == "roms":
        model = roms_model.roms(url)
    elif grid_type == "rect":
        model = rect_model.rect(url)
    
    model.get_dimensions(var_map)
    model.subset([south_lat,west_lon,north_lat,east_lon])
    
    #until I add time selection -- return last 10 time steps
    tlen = len(model.time)
    
    fn = model_name + '.nc'
    fp = os.path.join(temp_files_dir,fn)
    model.write_nc(var_map,fp,t_index=[tlen-10,tlen,1])
    
    return fn,fp
    